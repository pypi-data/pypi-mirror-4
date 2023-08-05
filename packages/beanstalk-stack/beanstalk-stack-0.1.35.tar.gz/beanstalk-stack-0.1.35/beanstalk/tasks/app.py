import json
import os
from fabric.api import *
from fabric.colors import *
from fabric.contrib.console import confirm
from netaddr import IPNetwork, AddrFormatError
from ground_soil.fabric import eval_kwargs
from ground_soil.filesystem import temporary_directory, rsync
from beanstalk import IDENTIFIER as beanstalk_identifier, BEANSTALK_LOCAL_BASE_PATH
import beanstalk
from beanstalk.tasks.utils import (set_verbose_level, load_role_settings as load_beanstalk_settings,
                                   load_web_servers, run_hooked_actions)
from beanstalk.decorators import beanstalk_role
from beanstalk.titles import section_title, tool_title
from beanstalk.validator import validate_web_server, validate_file_existence


@task
def web_server(*servers):
    """Set targeted web server
    :param servers: list of severs (IP, CIDR, or domain name)
    """
    hosts = []
    for server in servers:
        try:
            hosts += map(lambda x: '%s' % x, list(IPNetwork(server)))
        except (ValueError, AddrFormatError):
            hosts.append(server)

    user_hosts = []
    for host in hosts:
        puts('Add "%s" to web server list' % host)
        user_hosts.append(host)

    if 'web_servers' not in env.roledefs:
        env.roledefs['web_servers'] = list(set(user_hosts))
    else:
        env.roledefs.update({
            'web_servers': list(set(env.roledefs['web_servers'] + user_hosts))
        })


@task
def plant(VERBOSE=0):
    """plant beanstalk-stack for project in current work directory
    """
    print magenta('Beanstalk-Stack app plant tool')
    print '=-' * 40
    # Get values
    setting_values = [
        (
            'PROJECT_SOURCE_ROOT',
            prompt('Project Source Root?', default=os.getcwd()),
            os.getcwd(),
            'str',
        ),
        (
            'PROJECT_NAME',
            prompt('Project Name?', default=os.path.split(os.getcwd())[-1]),
            os.path.split(os.getcwd())[-1],
            'str',
        ),
        (
            'GIT_IGNORE_PATH',
            prompt('Where\'s git ignore file?', default='.gitignore', validate=validate_file_existence),
            '.gitignore',
            'str',
        ),
        (
            'WEB_SERVERS',
            prompt('Where to deploy? (Python list/tuple with server address)', validate=validate_web_server),
            None,
            'obj',
        ),
    ]
    print ''

    set_verbose_level(VERBOSE)

    # Create beanstalk_stack home
    beanstalk_local_base_path = os.path.normpath(os.path.join(os.getcwd(), BEANSTALK_LOCAL_BASE_PATH))
    if not os.path.exists(beanstalk_local_base_path):
        print cyan('Make beanstalk_stack local base: ./%s' % os.path.relpath(beanstalk_local_base_path))
        local('mkdir -p %s' % beanstalk_local_base_path)

    # Generate beanstalk_settings
    app_settings_path = os.path.normpath(os.path.join(beanstalk_local_base_path, 'beanstalk_app_settings.py'))
    if not os.path.exists(app_settings_path):
        print cyan('Generate beanstalk_stack app settings')
        with open(os.path.join(beanstalk_local_base_path, 'beanstalk_app_settings.py'), 'w') as f:
            for key, value, default, type in setting_values:
                if value != default:
                    f.write('%s = %s\n' % (key, value if type == 'obj' else '\'%s\'' % value))

    print green('Planted. Grow up now!')


@task
@beanstalk_role('app')
def deploy(settings_path=None, **settings_patches):
    """Deploy project in current work folder to beanstalk-stack
    """
    # Set variables
    env.work_directory = os.getcwd()

    # Load beanstalk settings
    settings_patches = eval_kwargs(settings_patches)
    beanstalk_settings = load_beanstalk_settings(local_settings_path=settings_path, **settings_patches)

    # Get variables from settings
    project_name = beanstalk_settings['PROJECT_NAME']
    project_source_root = beanstalk_settings['PROJECT_SOURCE_ROOT']

    # Setup environment, ssh, and web servers
    set_verbose_level()
    env.use_ssh_config = beanstalk_settings['USE_SSH_CONFIG']
    env['shell_env'] = beanstalk_settings['REMOTE_ENVIRONMENTS']
    load_web_servers()

    # Start
    print tool_title('Beanstalk-Stack app deploy tool')
    print '=-' * 40
    print 'Project Name   : ' + green(project_name)
    print 'Source root    : ' + green(project_source_root)
    print 'Target servers : ' + yellow('%s' % env.roledefs['web_servers'])
    print '-' * 80

    # Start to work in room!
    with temporary_directory(identifier=beanstalk_identifier, prefix='deploy~%s~' % project_name) as tmp_directory:
        print section_title('Copy source root to temp directory')
        puts('tmp dir: %s' % tmp_directory)
        env.temp_directory = tmp_directory

        # Find the exclude file (gitignore)
        gitignore_path = beanstalk_settings['GIT_IGNORE_PATH']
        gitignore_at_source_root = gitignore_path == '.gitignore'
        gitignore_path = os.path.normpath(os.path.join(project_source_root, gitignore_path))
        if os.path.exists(os.path.join(project_source_root, beanstalk_settings['GIT_IGNORE_PATH'])):
            # Copy the ignore to source root
            if not gitignore_at_source_root:
                local(rsync(gitignore_path, os.path.join(tmp_directory, '.gitignore')))
        else:
            abort('Cannot find gitignore file at %s' % gitignore_path)

        # Copy it
        rsync_argument = '-rlpctzD --exclude .git --exclude-from \'%s\'' % os.path.relpath(gitignore_path)
        local(rsync(project_source_root, tmp_directory, rsync_argument=rsync_argument, expand_to_destination=True))

        # Go to the tmp work dir
        with lcd(tmp_directory):
            puts(section_title('Switch to %s' % tmp_directory))

            # We wanna preserve pyc/pyo files in our remote
            # Remove *.pyc, *.pyo, *.py[co] in ignore patterns and append "logs/" in the ignore file
            local(
                'sed -i.bak -e \'/^\*\.py[c|o]$/d;/^\*\.py\[co\]$/d;$a\\\nlogs\/;$a\\\nvenv\/\' %s && rm -rf %s.bak' %
                ('.gitignore', '.gitignore')
            )

            # Check source code first
            run_hooked_actions('SOURCE_CHECK_ACTIONS')

            # Ask
            # TODO: Authenticate if possible
            if beanstalk_settings['CONFIRM_BEFORE_DEPLOY']:
                try:
                    if not confirm('deploy?', default=False):
                        raise KeyboardInterrupt
                except KeyboardInterrupt:
                    abort(red('User cancels deployment ...', bold=True))
                print ''

            # Call pre-deploy script
            if run_hooked_actions('PRE_DEPLOY_ACTIONS'):
                print ''

            # Work on remote
            print '+' * 80
            with settings(hide('running')):
                execute(deploy_remote_core)

            # Call post-deploy script
            if run_hooked_actions('POST_DEPLOY_ACTIONS'):
                print ''

            print green('Deployed!')


@roles('web_servers')
@beanstalk_role('app')
def deploy_remote_core():
    """ The part to run on each server
    """
    env.host_name = host_name = env.host_string.split('@')[-1]
    print section_title('Deploy to %s' % white(host_name))

    # Find Jack first
    with settings(hide('everything'), warn_only=True):
        if run('which bsjack').return_code != 0:
            abort(
                red('Hey! I cannot find Jack at ') + red(host_name, bold=True) + red('. ') +
                'Please setup beanstalk-stack on this server first.'
            )
        remote_bs_version = json.loads(run('bsjack info.version:USE_JSON=True --hide=status'))
        if beanstalk.VERSION != tuple(remote_bs_version['list']):
            abort(red('Hey! Jack at the remote is not the same as me. He\'s %s. But I\'m %s.') %
                  (remote_bs_version['string'], beanstalk.__version__))

    # Get/Set variables
    beanstalk_settings = env.beanstalk_settings
    project_name = beanstalk_settings['PROJECT_NAME']
    verbose_level = beanstalk_settings['VERBOSE']

    # Create this app to server
    print section_title('Find room for %s' % project_name)
    run('bsjack server.create_app:%s,VERBOSE=%d --hide=status' % (project_name, beanstalk_settings['VERBOSE']))

    # Call pre-install script
    run_hooked_actions('PRE_INSTALL_ACTIONS')

    # Get app info first
    with hide('everything'):
        app_info = json.loads(run('bsjack server.app_info:%s,VERBOSE=%d,USE_JSON=True --hide=status' %
                                  (project_name, beanstalk_settings['VERBOSE'])))
    env.remote_app_info = app_info
    remote_base_path = app_info['path']['base']
    remote_source_path = app_info['path']['source']

    print section_title('Send %s to remote: %s' % (project_name, white(remote_base_path)))
    # Send code
    rsync_argument = '-DLhrctz --delete --delete-excluded'
    rsync_argument += ' --exclude \'*.pyc\' --exclude \'*.pyo\' --exclude-from \'.gitignore\''
    if verbose_level == 0:
        rsync_argument += ' -q'
    elif verbose_level == 2:
        rsync_argument += ' -v'
    elif verbose_level == 3:
        rsync_argument += ' -Pv'
    target_source_path = 'beanstalk@%s:%s' % (host_name, remote_source_path)
    target_base_path = 'beanstalk@%s:%s' % (host_name, remote_base_path)
    local(rsync(env.temp_directory, target_source_path, rsync_argument=rsync_argument, expand_to_destination=True))
    local(rsync('%s/.gitignore' % env.temp_directory, target_base_path))

    # Call post-install script
    run_hooked_actions('POST_SEND_ACTIONS')

    # Update this app in server
    print section_title('Install %s in remote' % project_name)
    run('bsjack server.install_app:%s,VERBOSE=%d --hide=status' % (project_name, beanstalk_settings['VERBOSE']))

    # Call post-install script
    run_hooked_actions('POST_INSTALL_ACTIONS')

    # Commit state to git repo
    print section_title('Commit %s in remote' % project_name)
    run('bsjack server.commit_app:%s,VERBOSE=%d --hide=status' % (project_name, beanstalk_settings['VERBOSE']))
    run('bsjack server.reload_app:%s,VERBOSE=%d --hide=status' % (project_name, beanstalk_settings['VERBOSE']))

    print ' . ' * 26

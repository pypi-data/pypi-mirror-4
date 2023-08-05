import cStringIO as StringIO
import json
import os
import datetime
from fabric.api import *
from fabric.colors import *
from fabric.contrib.console import confirm
from netaddr import IPNetwork, AddrFormatError
from ground_soil.fabric import eval_kwargs
from ground_soil.filesystem import temporary_directory, rsync
from beanstalk import (IDENTIFIER as beanstalk_identifier, BEANSTALK_LOCAL_BASE_PATH,
                       __version__ as beanstalk_version_string, VERSION as beanstalk_version_tuple)
from beanstalk.tasks.utils import set_verbose_level, load_role_settings, load_web_servers, run_hooked_actions
from beanstalk.decorators import beanstalk_task
from beanstalk.console.titles import section_title, tool_title, separator
from beanstalk.validator import validate_web_server, validate_file_existence, validate_project_type, supported_projects


@beanstalk_task(beanstalk_role='app')
def web_server(*servers):
    """Set targeted web server
    :param servers: list of severs (IP, CIDR, or domain name)
    """
    hosts = []
    for server in servers:
        try:
            hosts += map(lambda x: '{0}'.format(x), list(IPNetwork(server)))
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


@beanstalk_task(beanstalk_role='app')
def plant(VERBOSE=0):
    """plant beanstalk-stack for project in current work directory
    """
    set_verbose_level(VERBOSE)
    # Create beanstalk_stack home
    beanstalk_local_base_path = os.path.normpath(os.path.join(os.getcwd(), BEANSTALK_LOCAL_BASE_PATH))
    app_settings_path = os.path.normpath(os.path.join(beanstalk_local_base_path, 'app_settings.py'))

    if not os.path.exists(beanstalk_local_base_path):
        print cyan('Make beanstalk_stack local base: ./{path}'.format(path=os.path.relpath(beanstalk_local_base_path)))
        local('mkdir -p {path}'.format(path=beanstalk_local_base_path))

    print magenta('Beanstalk-Stack app plant tool')
    print separator('=-')

    result = {}

    def collector(setting_sets):
        for setting_item in setting_sets:
            if setting_item is None:
                print separator()
                continue
            key, question, validator, value_type = setting_item
            default_value = beanstalk_default_settings[key] or ''
            value = prompt(question, default=default_value, validate=validator)
            if value != default_value:
                result[key] = (value, value_type)

        for key, (value, value_type) in result.items():
            beanstalk_default_settings[key] = value

    # Collect
    beanstalk_default_settings = load_role_settings(default_only=True)
    setting_set1 = [
        ('PROJECT_SOURCE_ROOT', 'Project Source Root?', None, 'str'),
        ('PROJECT_NAME', 'Project Name?', None, 'str'),
        ('GIT_IGNORE_PATH', 'Where\'s git ignore file?', validate_file_existence, 'str'),
        None,
        ('WEB_SERVERS', 'Where to deploy? (Python list/tuple with server address)', validate_web_server, 'obj'),
        None,
        ('PROJECT_TYPE',
         'Which project type you are? (\'plain\' for project not in ({projects}))'.format(
             projects=', '.join(supported_projects)),
         validate_project_type, 'str'),
    ]
    collector(setting_set1)

    # Project type
    if ('PROJECT_TYPE' in result and result['PROJECT_TYPE'] == 'django') or ('PROJECT_TYPE' not in result):
        setting_set2 = [
            ('DJANGO_PROJECT_SETTINGS', 'Where\'s your django project settings? (normal one)',
             validate_file_existence, 'str'),
            ('DJANGO_PROJECT_SETTINGS_DEV', 'Where\'s your django project settings for development?',
             validate_file_existence, 'str'),
            ('DJANGO_PROJECT_SETTINGS_PROD', 'Where\'s your django project settings for production?',
             validate_file_existence, 'str'),
        ]
        collector(setting_set2)

    print ''

    # Generate beanstalk_settings
    print cyan('Generate beanstalk_stack app settings')
    sorted_result = []
    for key, (value, value_type) in result.items():
        sorted_result.append((key, (value, value_type)))
    sorted_result.sort(cmp=lambda x, y: cmp(x[0], y[0]))

    print 'Genreated setting file:'
    print separator('=')
    output = StringIO.StringIO()
    for key, (value, value_type) in sorted_result:
        value = value if value_type == 'obj' else '\'{0}\''.format(value)
        output.write('{0} = {1}\n'.format(key, value))
    final_settings = output.getvalue()
    print final_settings
    output.close()
    print separator('=')

    write_to_file = confirm('Write to {path}'.format(path=app_settings_path), default=True)
    if write_to_file:
        if os.path.exists(app_settings_path):
            local('mv {path} {path}.bak.{ts}'.format(
                path=app_settings_path, ts=datetime.datetime.now().strftime('%s-%f')))
        with open(app_settings_path, 'w') as f:
            f.write(final_settings)

    print green('Planted. Grow up now!')


@beanstalk_task(beanstalk_role='app')
def deploy(settings_path=None, **settings_patches):
    """Deploy project in current work folder to beanstalk-stack
    """
    # Set variables
    env.work_directory = os.getcwd()
    env.in_remote = False

    # Load beanstalk settings
    settings_patches = eval_kwargs(settings_patches)
    beanstalk_settings = load_role_settings(additional_settings_path=settings_path, **settings_patches)

    # Get variables from settings
    project_name = beanstalk_settings['PROJECT_NAME']
    project_source_root = beanstalk_settings['PROJECT_SOURCE_ROOT']

    # Setup environment, ssh, and web servers
    set_verbose_level()
    env.use_ssh_config = beanstalk_settings['USE_SSH_CONFIG']
    env.shell_env = beanstalk_settings['REMOTE_ENVIRONMENTS']
    load_web_servers()

    # Start
    print tool_title('Beanstalk-Stack app deploy tool')
    print separator('=-')
    print 'Project Name   : ' + green(project_name)
    print 'Source root    : ' + green(project_source_root)
    print 'Target servers : ' + yellow('{0!s}'.format(env.roledefs['web_servers']))
    print separator('-')

    # Start to work in room!
    tmp_dir_prefix = 'deploy~{0}~'.format(project_name)
    with temporary_directory(identifier=beanstalk_identifier, prefix=tmp_dir_prefix) as tmp_directory:
        print section_title('Copy source root to temp directory')
        puts('tmp dir: {path}'.format(path=tmp_directory))
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
            abort('Cannot find gitignore file at {path}'.format(path=gitignore_path))

        # Copy it
        rsync_argument = '-rLpctzD --exclude .git --exclude-from \'{path}\''.format(
            path=os.path.relpath(gitignore_path))
        local(rsync(project_source_root, tmp_directory, rsync_argument=rsync_argument, expand_to_destination=True))

        # Go to the tmp work dir
        with lcd(tmp_directory):
            puts(section_title('Switch to {path}'.format(path=tmp_directory)))

            # We wanna preserve pyc/pyo files in our remote
            # Remove *.pyc, *.pyo, *.py[co] in ignore patterns and append "logs/" in the ignore file
            local(
                'sed -i.bak -e '
                '\'/^\*\.py[c|o]$/d;/^\*\.py\[co\]$/d;$a\\\nlogs\/;$a\\\nvenv\/\''
                ' {path} && rm -rf {path}.bak'.format(path='.gitignore')
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
            print separator('+')
            with settings(hide('running')):
                env.in_remote = True
                execute(deploy_remote_core)
                env.in_remote = False
            print separator('+')
            print ''

            # Call post-deploy script
            if run_hooked_actions('POST_DEPLOY_ACTIONS'):
                print ''

            print green('Deployed!')


@beanstalk_task(beanstalk_role='app')
@roles('web_servers')
def deploy_remote_core():
    """ The part to run on each server
    """
    env.host_name = host_name = env.host_string.split('@')[-1]
    print section_title('Deploy to {host}'.format(host=white(host_name)))

    # Find Jack first
    with settings(hide('everything'), warn_only=True):
        bs_version_result = run('bsjack info.version:USE_JSON=True --hide=status')
        if bs_version_result.failed:
            abort(
                red('Hey! I cannot find Jack at ') + red(host_name, bold=True) + red('. ') +
                'Please setup beanstalk-stack on this server first.'
            )
        remote_bs_version = json.loads(bs_version_result)
        if beanstalk_version_tuple != tuple(remote_bs_version['list']):
            abort(red('Hey! Jack at the remote is not the same as me. He\'s {0}. But I\'m {1}.').format(
                remote_bs_version['string'], beanstalk_version_string))

    # Get/Set variables
    beanstalk_settings = env.beanstalk_settings
    project_name = beanstalk_settings['PROJECT_NAME']
    verbose_level = beanstalk_settings['VERBOSE']

    # Call pre-install script
    run_hooked_actions('PRE_INSTALL_ACTIONS')

    # Create this app to server
    print section_title('Find room for {name} in {host}'.format(name=project_name, host=host_name))
    run('bsjack server.create_app:{project_name},VERBOSE={verbose:d} --hide=status'.format(
        project_name=project_name, verbose=beanstalk_settings['VERBOSE']))

    # Get app info first
    with hide('everything'):
        app_info = json.loads(
            run(
                'bsjack server.app_info:{project_name},VERBOSE={verbose:d},USE_JSON=True --hide=status'.format(
                    project_name=project_name, verbose=beanstalk_settings['VERBOSE'])))
    env.remote_app_info = app_info
    remote_base_path = app_info['path']['base']
    remote_source_path = app_info['path']['source']

    # Call pre-install script
    run_hooked_actions('PRE_SEND_ACTIONS')

    print section_title('Send {name} to remote: {path}'.format(name=project_name, path=white(remote_base_path)))
    # Send code
    rsync_argument = '-DLhrctz --delete --delete-excluded'
    rsync_argument += ' --exclude \'*.pyc\' --exclude \'*.pyo\' --exclude-from \'.gitignore\''
    if verbose_level == 0:
        rsync_argument += ' -q'
    elif verbose_level == 2:
        rsync_argument += ' -v'
    elif verbose_level == 3:
        rsync_argument += ' -Pv'
    target_source_path = 'beanstalk@{0}:{1}'.format(host_name, remote_source_path)
    target_base_path = 'beanstalk@{0}:{1}'.format(host_name, remote_base_path)
    local(rsync(env.temp_directory, target_source_path, rsync_argument=rsync_argument, expand_to_destination=True))
    local(rsync('{path}/.gitignore'.format(path=env.temp_directory), target_base_path))

    # Call post-install script
    run_hooked_actions('POST_SEND_ACTIONS')

    # Update this app in server
    print section_title('Install %s in remote' % project_name)
    run('bsjack server.install_app:{name},VERBOSE={verbose:d} --hide=status'.format(
        name=project_name, verbose=beanstalk_settings['VERBOSE']))

    # Call post-install script
    run_hooked_actions('POST_INSTALL_ACTIONS')

    # Commit state to git repo
    print section_title('Commit %s in remote' % project_name)
    run('bsjack server.commit_app:{name},VERBOSE={verbose:d} --hide=status'.format(
        name=project_name, verbose=beanstalk_settings['VERBOSE']))
    run('bsjack server.reload_app:{name},VERBOSE={verbose:d} --hide=status'.format(
        name=project_name, verbose=beanstalk_settings['VERBOSE']))

    url = 'http://{host}/{project_name}/'.format(host=host_name, project_name=project_name)  # TODO: URL from remote
    print '{host} is finished. URL is {url}'.format(host=host_name, url=blue(url))

    print separator(' . ')


@beanstalk_task(beanstalk_role='app')
def activate(settings_path=None, **settings_patches):
    """Activate apps in the remote
    """
    beanstalk_settings = load_role_settings(additional_settings_path=settings_path, **settings_patches)
    set_verbose_level()
    load_web_servers()

    project_name = beanstalk_settings['PROJECT_NAME']

    @roles('web_servers')
    def core():
        run('bsjack server.activate_app:{project_name}'.format(project_name=project_name))
    execute(core)


@beanstalk_task(beanstalk_role='app')
def deactivate(settings_path=None, **settings_patches):
    """Deactivate apps in the remote
    """
    beanstalk_settings = load_role_settings(additional_settings_path=settings_path, **settings_patches)
    set_verbose_level()
    load_web_servers()

    project_name = beanstalk_settings['PROJECT_NAME']

    @roles('web_servers')
    def core():
        run('bsjack server.deactivate_app:{project_name}'.format(project_name=project_name))
    execute(core)

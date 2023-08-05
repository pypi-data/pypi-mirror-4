import datetime
import json
import os
import socket
from fabric.api import *
from fabric.colors import *
from fabric.contrib.console import confirm
from ground_soil.fabric import eval_kwargs, virtual_env
from ground_soil.filesystem import temporary_directory, edit_file
from beanstalk import IDENTIFIER
from beanstalk.decorators import beanstalk_role
from beanstalk.tasks.utils import load_role_settings as load_beanstalk_settings, set_verbose_level
from beanstalk.titles import tool_title, section_title


def project_base_path(project_name):
    beanstalk_settings = env.get('beanstalk_settings', None)
    if beanstalk_settings is None:
        abort('Load beanstalk settings first')

    beanstalk_stack_base = beanstalk_settings['BEANSTALK_STACK_BASE']
    project_base = os.path.abspath(os.path.join(beanstalk_stack_base, 'apps/', project_name))

    return project_base


def project_source_path(project_name):
    project_base = project_base_path(project_name)
    return os.path.join(project_base, 'source/')


def project_logs_path(project_name):
    project_base = project_base_path(project_name)
    return os.path.join(project_base, 'logs/')


def project_venv_path(project_name):
    project_base = project_base_path(project_name)
    return os.path.join(project_base, 'venv/')


def project_uwsgi_path(project_name):
    project_base = project_base_path(project_name)
    return os.path.join(project_base, 'uwsgi.ini')


def apache_conf_path():
    beanstalk_settings = env.get('beanstalk_settings', None)
    if beanstalk_settings is None:
        abort('Load beanstalk settings first')

    beanstalk_stack_base = beanstalk_settings['BEANSTALK_STACK_BASE']
    return os.path.join(beanstalk_stack_base, 'confs/', 'apache.conf')


def apps_pool_path():
    beanstalk_settings = env.get('beanstalk_settings', None)
    if beanstalk_settings is None:
        abort('Load beanstalk settings first')

    beanstalk_stack_base = beanstalk_settings['BEANSTALK_STACK_BASE']
    return os.path.join(beanstalk_stack_base, 'apps/', 'apps.json')


# Tasks
#-----------------------------------------------------------------------------------------------------------------------


@task
@beanstalk_role('server')
def setup(settings_path=None, **settings_patches):
    """Setup remote base of beanstalk-stack in this server
    """
    print tool_title('Beanstalk-stack server setup tool')
    print ''

    # Load beanstalk settings
    settings_patches = eval_kwargs(settings_patches)
    beanstalk_settings = load_beanstalk_settings(local_settings_path=settings_path, **settings_patches)
    beanstalk_stack_base = beanstalk_settings['BEANSTALK_STACK_BASE']
    set_verbose_level()

    # Install packages for building uwsgi
    print section_title('Install system packages')
    local('yum install -y python-devel sqlite-devel libxml2-devel pcre-devel zeromq-devel'
          ' libcap-devel libuuid-devel libev-devel python-greenlet-devel httpd-devel')

    # Install Uwsgi
    with temporary_directory(identifier=IDENTIFIER, prefix='init_remote_base') as tmp_directory:
        with lcd(tmp_directory):
            print section_title('Install uwsgi and mod_uwsgi')
            # Get source code
            local('wget http://projects.unbit.it/downloads/uwsgi-lts.tar.gz')
            local('tar -zxf uwsgi-lts.tar.gz')
            try:
                uwsgi_src_folder = [path for path in os.listdir(tmp_directory)
                                    if path.startswith('uwsgi-') and '-lts' not in path][0]
            except IndexError:
                abort('Failed to extract uwsgi source folder')
                return

            with lcd(uwsgi_src_folder):
                # Create build configuration
                local('mkdir -p /usr/local/lib/uwsgi')
                local('echo "[uwsgi]" >> buildconf/beanstalk.ini')
                local('echo "main_plugin = python" >> buildconf/beanstalk.ini')
                local('echo "inherit = base" >> buildconf/beanstalk.ini')
                local('echo "plugin_dir = /usr/local/lib/uwsgi" >> buildconf/beanstalk.ini')
                # Build and install
                local('python uwsgiconfig.py --build beanstalk')
                local('cp uwsgi /usr/local/bin/uwsgi')
                if not os.path.exists('/usr/bin/uwsgi'):
                    local('ln -s /usr/local/bin/uwsgi /usr/bin/uwsgi')
                # mod_uwsgi
                local('apxs -i -c apache2/mod_uwsgi.c')
                local('echo "LoadModule uwsgi_module modules/mod_uwsgi.so" > /etc/httpd/conf.d/uwsgi.conf')
                # Beanstalk
                local('echo "Include %s" > /etc/httpd/conf.d/beanstalk.conf' % apache_conf_path())
                # Restart apache
                local('/etc/init.d/httpd reload')

    # Do you have user "beanstalk"?
    with settings(hide('everything'), warn_only=True):
        has_beanstalk_user = local('egrep ^beanstalk: /etc/passwd').return_code == 0
    if not has_beanstalk_user:
        print section_title('Create user "beanstalk"')
        # Create user
        local('useradd beanstalk')
        # Setup user password
        print yellow('Set password for user beanstalk', bold=True)
        local('passwd beanstalk')
        # Setup git
        local('su -c "git config --global user.name \'beanstalk\'" - beanstalk')
        local('su -c "git config --global user.email beanstalk@beanstalk-stack.com" - beanstalk')
        # Setup .ssh
        local('mkdir -p ~beanstalk/.ssh')
        local('chmod 700 ~beanstalk/.ssh')
        local('touch ~beanstalk/.ssh/authorized_keys')
        local('chmod 644 ~beanstalk/.ssh/authorized_keys')
        local('chown -R beanstalk:beanstalk ~beanstalk/.ssh')

    # Apache command
    print section_title('Create apache-reload command')
    httpd_cmd_path = '/usr/sbin/httpd_reload'
    with open(httpd_cmd_path, 'w') as f:
        f.write('#!/bin/sh\n')
        f.write('service httpd reload')
    local('chmod +x %s' % httpd_cmd_path)
    # Give beanstalk permission
    sudoer_file = '/etc/sudoers.d/beanstalk_reload_httpd'
    with open(sudoer_file, 'w') as f:
        f.write('beanstalk ALL=(root) NOPASSWD: %s' % httpd_cmd_path)
    local('chmod 440 %s' % sudoer_file)

    # Make beanstalk access ssh
    local('sed -i.bak -e "/^AllowGroups wheel$/cAllowGroups wheel beanstalk" /etc/ssh/sshd_config')

    # Apache conf
    local('echo "# Beanstalk Apache conf" > %s' % apache_conf_path())
    local('chown beanstalk:beanstalk %s' % apache_conf_path())

    # Create homebase
    print section_title('Deploy target is: %s' % beanstalk_stack_base)
    local('mkdir -p %s' % beanstalk_stack_base)
    local('mkdir -p %s' % os.path.join(beanstalk_stack_base, 'global-logs'))
    local('mkdir -p %s' % os.path.join(beanstalk_stack_base, 'apps'))
    local('mkdir -p %s' % os.path.join(beanstalk_stack_base, 'confs'))
    local('echo "{}" >> %s' % apps_pool_path())
    local('chmod o+rx %s' % beanstalk_stack_base)
    local('chown -R beanstalk:beanstalk %s' % beanstalk_stack_base)

    local('/etc/init.d/sshd restart')
    local('/etc/init.d/httpd reload')


@task
@beanstalk_role('server')
def create_app(project_name, settings_path=None, **settings_patches):
    """Create an app
    """
    settings_patches = eval_kwargs(settings_patches)
    load_beanstalk_settings(local_settings_path=settings_path, **settings_patches)
    set_verbose_level()

    # Folder paths
    project_base = project_base_path(project_name)
    project_source = project_source_path(project_name)
    project_logs = project_logs_path(project_name)
    project_venv = project_venv_path(project_name)

    if os.path.exists(project_base):
        print 'Nothing to do. App existed!'
        return

    # Create folders
    print section_title('Create folders')
    local('mkdir -p %s' % project_base)
    local('mkdir -p %s' % project_source)
    local('mkdir -p %s' % project_logs)

    # Initialize venv
    if not os.path.exists(project_venv):
        print section_title('Initialize virtual env')
        with lcd(project_base):
            local('virtualenv venv')

    # Initialize git
    if not os.path.exists(os.path.join(project_base, '.git')):
        print section_title('Make git repository')
        with lcd(project_base):
            local('git init')
            local('touch .gitignore')
            local('git add .gitignore')
            local('git commit -m "Init commit"')

    # Apps pool
    with open(apps_pool_path(), 'r') as f:
        apps_pool = json.loads(f.read())

    # Get uwsgi port
    uwsgi_port = None
    if project_name in apps_pool:
        uwsgi_port = apps_pool[project_name]['uwsgi']['port']
    else:
        app_ports = [app['uwsgi']['port'] for name, app in apps_pool.items()]
        if len(app_ports) == 0:
            uwsgi_port = 50000  # >= 49152
        else:
            try_times = 1
            while try_times <= 10:
                try:
                    uwsgi_port = max(app_ports) + try_times
                    s = socket.socket()
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind(('localhost', uwsgi_port))
                    break
                except socket.error:
                    uwsgi_port = None
                    try_times += 1
    if uwsgi_port is None:
        abort('No available port')

    def editor(pool):
        pool[project_name] = {
            'path': {
                'base': project_base,
                'source': project_source,
                'logs': project_logs,
                'venv': project_venv,
            },
            'uwsgi': {
                'port': uwsgi_port,
            },
        }
        return pool
    print section_title('Add app to app_pool')
    edit_file(apps_pool_path(), editor=editor)

    print section_title('Add to apache httpd')
    with open(apache_conf_path(), 'r') as f:
        apache_conf = f.read()
    if not '# %s' % project_name in apache_conf:
        commands = [
            '# %s' % project_name,
            '#' + '-' * 20,
            '<Location /%s>' % project_name,
            '    SetHandler uwsgi-handler',
            '    uWSGISocket 127.0.0.1:%s' % uwsgi_port,
            '</Location>',
            '#' + '-' * 20,
            ' ',
        ]
        sed_command = '\\\n'.join(commands)
        local('sed -i.bak -e \'$a\\%s\' %s && rm -rf %s.bak' % (sed_command, apache_conf_path(), apache_conf_path()))


@task
@beanstalk_role('server')
def delete_app(project_name, settings_path=None, **settings_patches):
    """Delete an app
    """
    settings_patches = eval_kwargs(settings_patches)
    load_beanstalk_settings(local_settings_path=settings_path, **settings_patches)
    set_verbose_level()

    # Folder paths
    project_base = project_base_path(project_name)

    remove = confirm(red('Remove project: %s ?' % project_name), default=False)

    # delete
    if remove:
        print section_title('Remove app @ %s' % project_base)
        local('rm -rf %s' % project_base)

        def editor(apps_pool):
            if project_name in apps_pool:
                del apps_pool[project_name]
            return apps_pool
        edit_file(apps_pool_path(), editor)

    local('sed -i.bak -e \'/# %s/,+7d\' %s && rm -rf %s.bak' % (project_name, apache_conf_path(), apache_conf_path()))


@task
@beanstalk_role('server')
def update_app(project_name, settings_path=None, **settings_patches):
    """Update an app (call when u updated the code)
    """
    settings_patches = eval_kwargs(settings_patches)
    load_beanstalk_settings(local_settings_path=settings_path, **settings_patches)
    set_verbose_level()

    project_source = project_source_path(project_name)
    project_venv = project_venv_path(project_name)

    print section_title('Install/Update packages in virtualenv')
    with settings(virtual_env(project_venv)):
        local('pip install -r %s' % os.path.join(project_source, 'requirements.txt'))

    print section_title('Compile python code')
    local('find %s -name \'*.pyc\' -exec rm -rf {} \;' % project_source)
    local('find %s -name \'*.pyo\' -exec rm -rf {} \;' % project_source)
    local('python -m compileall -q %s' % project_source)


@task
@beanstalk_role('server')
def reload_app(project_name, settings_path=None, **settings_patches):
    """Update an app (call when u updated the code)
    """
    settings_patches = eval_kwargs(settings_patches)
    load_beanstalk_settings(local_settings_path=settings_path, **settings_patches)
    set_verbose_level()

    print section_title('Reload app: %s' % project_name)
    local('touch %s' % project_uwsgi_path(project_name))


@task
@beanstalk_role('server')
def build_venv(project_name, settings_path=None, **settings_patches):
    """Build virtual env of target app.
    """
    settings_patches = eval_kwargs(settings_patches)
    load_beanstalk_settings(local_settings_path=settings_path, **settings_patches)
    set_verbose_level()

    # path
    project_venv = project_venv_path(project_name)
    requirments_path = os.path.join(project_source_path(project_name), 'requirments.txt')

    print section_title('Build virtualenv for %s' % project_name)

    # Clean it
    local('rm -rf %s' % project_venv)

    venv_base, venv_name = os.path.split(project_venv)
    with lcd(venv_base):
        local('virtualenv %s' % venv_name)
        with settings(virtual_env(project_venv)):
            local('pip intall -r %s' % requirments_path)


@task
@beanstalk_role('server')
def app_info(project_name, settings_path=None, **settings_patches):
    """Get info of an app
    """
    settings_patches = eval_kwargs(settings_patches)
    beanstalk_settings = load_beanstalk_settings(local_settings_path=settings_path, **settings_patches)
    set_verbose_level()

    with open(apps_pool_path(), 'r') as f:
        apps_pool = json.loads(f.read())

    # Gather information
    if project_name in apps_pool:
        apps = apps_pool[project_name]
    else:
        if beanstalk_settings.get('USE_JSON', False):
            print json.dumps({'error': 'No such app'})
        else:
            print red('No such app')
        return

    if beanstalk_settings.get('USE_JSON', False):
        result = apps
        json_string = json.dumps(result, separators=(',', ':'))

        if beanstalk_settings.get('PRINT_JSON', True):
            print json_string
        return json_string
    else:
        print section_title('Beanstalk-stack app: %s' % project_name)
        print '-=' * 40
        print 'Base   : %s' % apps['path']['base']
        print 'Source : %s' % apps['path']['source']
        print 'Logs   : %s' % apps['path']['logs']
        print 'venv   : %s' % apps['path']['venv']
        print '-' * 40
        print 'uwsgi port : %s' % apps['uwsgi']['port']


@task
@beanstalk_role('server')
def list_apps(settings_path=None, **settings_patches):
    """Get list of apps
    """
    settings_patches = eval_kwargs(settings_patches)
    load_beanstalk_settings(local_settings_path=settings_path, **settings_patches)
    set_verbose_level()

    with open(apps_pool_path(), 'r') as f:
        apps_pool = json.loads(f.read())
    apps = [key for key, value in apps_pool.items()]

    print section_title('Beanstalk-stack apps')
    print '-=' * 40
    for app in apps:
        print app


@task
@beanstalk_role('server')
def commit_app(project_name, processes=2, threads=20, settings_path=None, **settings_patches):
    """Get list of apps
    """
    settings_patches = eval_kwargs(settings_patches)
    load_beanstalk_settings(local_settings_path=settings_path, **settings_patches)
    set_verbose_level()

    project_base = project_base_path(project_name)
    with settings(lcd(project_base), hide('warnings'), warning=True):
        local('git add -A && git commit -m "state at %s"' % datetime.datetime.now().strftime('%s'))

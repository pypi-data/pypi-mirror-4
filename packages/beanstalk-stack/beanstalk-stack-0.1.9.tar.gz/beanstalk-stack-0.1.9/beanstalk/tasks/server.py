import os
from fabric.api import *
from fabric.colors import *
from soil.fabric import eval_kwargs
from soil.filesystem import temporary_directory
from beanstalk import IDENTIFIER
from beanstalk.decorators import beanstalk_role
from beanstalk.tasks.utils import load_role_settings as load_beanstalk_settings, set_verbose_level
from beanstalk.titles import tool_title, section_title


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
        f.write('beanstalk ALL=(root) NOPASSWD:%s' % httpd_cmd_path)
    local('chmod 440 %s' % sudoer_file)

    # Make beanstalk access ssh
    local('sed -i.bak -e "/^AllowGroups wheel$/cAllowGroups wheel beanstalk" /etc/ssh/sshd_config')
    local('/etc/init.d/sshd restart')

    # Create homebase
    print section_title('Deploy target is: %s' % beanstalk_stack_base)
    local('mkdir -p %s' % beanstalk_stack_base)
    local('chmod o+rx %s' % beanstalk_stack_base)
    local('chown beanstalk:beanstalk %s' % beanstalk_stack_base)


@task
@beanstalk_role('server')
def create_app(project_name, settings_path=None, **settings_patches):
    settings_patches = eval_kwargs(settings_patches)
    beanstalk_settings = load_beanstalk_settings(local_settings_path=settings_path, **settings_patches)
    beanstalk_stack_base = beanstalk_settings['BEANSTALK_STACK_BASE']
    set_verbose_level()

    # Folder paths
    remote_project_base = os.path.abspath(os.path.join(beanstalk_stack_base, project_name))
    remote_project_source = os.path.join(remote_project_base, 'source/')
    remote_project_logs = os.path.join(remote_project_base, 'logs/')
    remote_project_venv = os.path.join(remote_project_base, 'venv/')

    if os.path.exists(remote_project_base):
        return

    # Create folders
    local('mkdir -p %s' % remote_project_base)
    local('mkdir -p %s' % remote_project_source)
    local('mkdir -p %s' % remote_project_logs)

    # Initialize venv
    with lcd(remote_project_base):
        local('virtualenv venv')

    # Initialize git
    with lcd(remote_project_source):
        local('git init')


@task
@beanstalk_role('server')
def update_app(project_name):
    print 'update_app: %s' % project_name

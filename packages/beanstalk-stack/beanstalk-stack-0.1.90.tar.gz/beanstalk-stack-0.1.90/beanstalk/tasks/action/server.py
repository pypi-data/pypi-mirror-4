import os
from fabric.api import *
from ground_soil.fabric import virtual_env
from beanstalk.console.titles import action_title
from beanstalk.paths.server import project_venv_path, project_source_path, project_base_path


def create_database(db_name=None, db_user=None, db_password=None, permissions=None):
#    if permissions is None:
#        permissions = env.get(
#            'db_permissions',
#            ['SELECT', 'UPDATE', 'INSERT', 'DELETE', 'INDEX', 'CREATE', 'DROP', 'ALTER', 'REFERENCES'])
#    if db_name is None:
#        db_name = env.db_name
#    if db_user is None:
#        db_user = env.db_user
#    if db_password is None:
#        db_password = env.db_password
#
#    db_info = {
#        'db_name': db_name,
#        'db_user': db_user,
#        'db_password': db_password,
#        'db_perms': ', '.join(permissions),
#    }
#
#    sql_commands = [
#        'CREATE DATABASE IF NOT EXISTS {db_name}',
#        'GRANT {db_perms} ON {db_name}.* TO {db_user}@\'localhost\' IDENTIFIED BY \'{db_password}\'',
#        'FLUSH PRIVILEGES',
#    ]
#
#    for sql_command in sql_commands:
#        print sql_command.format(**db_info)
    pass


def install_pip_requirements():
    print action_title('Install/Update packages in virtualenv')

    project_name = env.project_name
    project_source = project_source_path(project_name)
    project_venv = project_venv_path(project_name)

    with settings(virtual_env(project_venv)):
        local('pip install -r %s' % os.path.join(project_source, 'requirements.txt'))


def compile_python_code():
    print action_title('Compile python code')

    project_name = env.project_name
    project_source = project_source_path(project_name)

    local('find %s -name \'*.pyc\' -exec rm -rf {} \;' % project_source)
    local('find %s -name \'*.pyo\' -exec rm -rf {} \;' % project_source)
    local('python -m compileall -q %s' % project_source)


def create_venv():
    project_name = env.project_name

    project_base = project_base_path(project_name)
    project_venv = project_venv_path(project_name)

    if not os.path.exists(project_venv):
        print action_title('Initialize virtual env')
        with lcd(project_base):
            local('virtualenv venv')


def initialize_git():
    project_name = env.project_name
    project_base = project_base_path(project_name)

    # Initialize git
    if not os.path.exists(os.path.join(project_base, '.git')):
        print action_title('Make git repository')
        with lcd(project_base):
            local('git init')
            local('touch .gitignore')
            local('git add .gitignore')
            local('git commit -m "Init commit"')


def install_yum_packages():
    beanstalk_settings = env.get('beanstalk_settings', None)
    if beanstalk_settings is None or not beanstalk_settings['ALLOW_INSTALL_YUM_PACKAGES']:
        return

    project_name = env.project_name
    project_source = project_source_path(project_name)
    yum_package_list_path = os.path.join(project_source, 'yum_packages.txt')
    if not os.path.exists(yum_package_list_path):
        return

    yum_packages = []
    with open(yum_package_list_path, 'r') as yum_package_list:
        for yum_package in yum_package_list:
            yum_packages.append(yum_package[:-1])

    yum_package_string = ' '.join(yum_packages)
    yum_command = 'sudo yum install {0}'.format(yum_package_string)
    local(yum_command)

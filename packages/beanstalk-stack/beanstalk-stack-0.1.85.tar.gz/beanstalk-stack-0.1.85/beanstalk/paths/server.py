import os
from fabric.state import env
from fabric.utils import abort


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


def project_run_path(project_name):
    project_base = project_base_path(project_name)
    return os.path.join(project_base, 'run/')


def project_logs_path(project_name):
    project_base = project_base_path(project_name)
    return os.path.join(project_base, 'logs/')


def project_venv_path(project_name):
    project_base = project_base_path(project_name)
    return os.path.join(project_base, 'venv/')


def project_uwsgi_path(project_name):
    project_source = project_source_path(project_name)
    return os.path.join(project_source, 'uwsgi.ini')


def apache_conf_path():
    beanstalk_settings = env.get('beanstalk_settings', None)
    if beanstalk_settings is None:
        abort('Load beanstalk settings first')

    beanstalk_stack_base = beanstalk_settings['BEANSTALK_STACK_BASE']
    return os.path.join(beanstalk_stack_base, 'confs/', 'apache.conf')

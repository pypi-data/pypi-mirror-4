import os
from fabric.api import *
from beanstalk.decorators import beanstalk_role
from beanstalk.tasks.action import action
from beanstalk.titles import action_title


@task
@beanstalk_role('app')
def collect_static():
    """Collect static files in a django project (Django 1.3+)
    """
    print action_title('Collect static files in Django project')
    verbose = env.beanstalk_settings['VERBOSE']
    action('python manage.py collectstatic --verbosity={0:d} --noinput'.format(verbose), chdir='source')()


@task
@beanstalk_role('app')
def sync_db():
    """Sync db
    """
    print action_title('Sync database')
    verbose = env.beanstalk_settings['VERBOSE']
    action('python manage.py syncdb --noinput -v {0:d}'.format(verbose), chdir='source')()


@task
@beanstalk_role('app')
def south_migrate():
    """Do a South migration
    """
    print action_title('Migrate database')
    verbose = env.beanstalk_settings['VERBOSE']
    action('python manage.py migrate --noinput -v {0:d}'.format(verbose), chdir='source')()


@task
@beanstalk_role('app')
def switch_settings():
    """Switch django settings to production one
    This implementation is designed for link-based settings file
    """
    print action_title('Switch to production settings')
    beanstalk_settings = env.beanstalk_settings
    source_root = env.remote_app_info['path']['source'] if env.in_remote else env.temp_directory
    django_settings = os.path.abspath(os.path.join(source_root, beanstalk_settings['DJANGO_PROJECT_SETTINGS']))
    prod_settings = os.path.abspath(os.path.join(source_root, beanstalk_settings['DJANGO_PROJECT_SETTINGS_PROD']))

    exec_command = run if env.in_remote else local
    exec_command('mv {settings} {settings}.bak'.format(settings=django_settings))
    exec_command('ln -s {prod_settings} {settings}'.format(prod_settings=prod_settings, settings=django_settings))
    exec_command('rm -rf {settings}.bak'.format(settings=django_settings))

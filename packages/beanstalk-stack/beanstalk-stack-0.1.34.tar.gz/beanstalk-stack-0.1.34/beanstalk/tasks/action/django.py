from fabric.api import *
from beanstalk.decorators import beanstalk_role
from beanstalk.tasks.utils import load_role_settings as load_beanstalk_settings
from beanstalk.titles import action_title


@task
@beanstalk_role('app')
def collect_static():
    """Collect static files in a django project (Django 1.3+)
    """
    print action_title('Collect static files in Django project')
    beanstalk_settings = load_beanstalk_settings()

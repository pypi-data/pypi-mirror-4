from beanstalk.tasks import app, server, users, info, utils, daemon
from beanstalk.decorators import beanstalk_task

settings = beanstalk_task(alias='settings')(utils.load_role_settings)

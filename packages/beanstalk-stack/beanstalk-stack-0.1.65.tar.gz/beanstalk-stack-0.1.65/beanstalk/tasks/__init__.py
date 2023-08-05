from fabric.api import task
from beanstalk.tasks import app, server, users, info, utils


settings = task(alias='settings')(utils.load_role_settings)

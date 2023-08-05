import os
import sys
from six import callable
from beanstalk.tasks.action import check_comments
from beanstalk.tasks.action.django import collect_static, sync_db, south_migrate, switch_settings


def _(var):
    return var() if callable(var) else var


# Local project information
#-----------------------------------------------------------------------------------------------------------------------
PROJECT_SOURCE_ROOT = lambda x: os.getcwd()  # PLANT
PROJECT_NAME = lambda x: os.path.split(_(x['PROJECT_SOURCE_ROOT']))[-1]  # PLANT
GIT_IGNORE_PATH = '.gitignore'  # PLANT
PROJECT_VENV_PATH = lambda x: os.path.abspath(sys.prefix)  # PLANT
PROJECT_TYPE = 'django'  # PLANT
DJANGO_PROJECT_SETTINGS = lambda x: os.path.join(_(x['PROJECT_NAME']), 'settings.py')  # PLANT
DJANGO_PROJECT_SETTINGS_DEV = lambda x: os.path.join(_(x['PROJECT_NAME']), 'dev_settings.py')  # PLANT
DJANGO_PROJECT_SETTINGS_PROD = lambda x: os.path.join(_(x['PROJECT_NAME']), 'prod_settings.py')  # PLANT

# Remote base information
#-----------------------------------------------------------------------------------------------------------------------
WEB_SERVERS = None  # required, PLANT
REMOTE_ENVIRONMENTS = {}

# Beanstalk tool behavior
#-----------------------------------------------------------------------------------------------------------------------
VERBOSE = 0
USE_SSH_CONFIG = True
CONFIRM_BEFORE_DEPLOY = True
# Source code check
CHECK_COMMENTS = True
CHECK_TODO = False
CHECK_NOTE = False
CHECK_FIX_ME = True

# Hooked actions
#-----------------------------------------------------------------------------------------------------------------------
default_source_check_actions = {
    'django': [check_comments],
}
default_pre_deploy_actions = {
    'django': [collect_static, switch_settings],
}
default_pre_install_actions = {}
default_pre_send_actions = {}
default_post_send_actions = {}
default_post_install_actions = {
    'django': [sync_db, south_migrate],
}
default_post_deploy_actions = {}

# Before confirmation of deploy
# Show issues or other warnings before doing someting to remote
SOURCE_CHECK_ACTIONS = lambda x: default_source_check_actions.get(_(x['PROJECT_TYPE']), [])
# Start to work.
# Before connect to remote. Actions will be performed once.
PRE_DEPLOY_ACTIONS = lambda x: default_pre_deploy_actions.get(_(x['PROJECT_TYPE']), [])
# We connected to the remote
# But we have done nothing yet.
PRE_INSTALL_ACTIONS = lambda x: default_pre_install_actions.get(_(x['PROJECT_TYPE']), [])
# We have remote app info now.
PRE_SEND_ACTIONS = lambda x: default_pre_send_actions.get(_(x['PROJECT_TYPE']), [])
# The source code has been just delivered.
# Beanstalk modifies your code to fit its settings after this stage.
# (For example, env information related to the rmote like uwsgi port.
POST_SEND_ACTIONS = lambda x: default_post_send_actions.get(_(x['PROJECT_TYPE']), [])
# The code has been cleared, modified, and normalized. You can perform db-migration here
POST_INSTALL_ACTIONS = lambda x: default_post_install_actions.get(_(x['PROJECT_TYPE']), [])
# Things are almost finished. You can do clean job here. They will be performed only once
POST_DEPLOY_ACTIONS = lambda x: default_post_deploy_actions.get(_(x['PROJECT_TYPE']), [])

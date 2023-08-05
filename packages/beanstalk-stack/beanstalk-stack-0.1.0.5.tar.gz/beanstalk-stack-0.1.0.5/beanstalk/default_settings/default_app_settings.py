import os
from beanstalk.tasks.action import check_comments

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
SOURCE_CHECK_ACTIONS = [
    check_comments,
]
PRE_DEPLOY_ACTIONS = []
PRE_INSTALL_ACTIONS = []
POST_INSTALL_ACTIONS = []
POST_DEPLOY_ACTIONS = []

# Local project information
#-----------------------------------------------------------------------------------------------------------------------
PROJECT_SOURCE_ROOT = lambda: os.getcwd()
PROJECT_NAME = lambda: os.path.split(PROJECT_SOURCE_ROOT())[-1]
GIT_IGNORE_PATH = '.gitignore'

# Remote base information
#-----------------------------------------------------------------------------------------------------------------------
WEB_SERVERS = []  # required
REMOTE_ENVIRONMENTS = {}

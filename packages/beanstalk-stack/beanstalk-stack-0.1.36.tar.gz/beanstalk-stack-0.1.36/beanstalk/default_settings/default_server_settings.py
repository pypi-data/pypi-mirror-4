def _(var):
    return var() if callable(var) else var


# Beanstalk tool behavior
#-----------------------------------------------------------------------------------------------------------------------
VERBOSE = 3

# Beanstalk Installation
#-----------------------------------------------------------------------------------------------------------------------
BEANSTALK_STACK_BASE = '/var/beanstalk'
STATIC_URL_PREFIX = 'static'
BEANSTALK_EMAIL = 'beanstalk@beanstalk-stack.com'

PRE_SETUP_ACTIONS = []  # Only beanstalk settings
POST_SETUP_ACTIONS = []  # Only beanstalk settings

PRE_CREATE_ACTIONS = []  # project_name
POST_CREATE_ACTIONS = []  # project_name, uwsgi_port

PRE_COMMIT_ACTIONS = []  # project_name
POST_COMMIT_ACTIONS = []  # project_name

PRE_RELOAD_ACTIONS = []  # project_name
POST_RELOAD_ACTIONS = []  # project_name

PRE_INSTALL_ACTIONS = []  # project_name
POST_INSTALL_ACTIONS = []  # project_name

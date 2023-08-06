from beanstalk.tasks.action.server import (create_database, install_pip_requirements, compile_python_code,
                                           create_venv, initialize_git, install_yum_packages)


def _(var):
    return var() if callable(var) else var


# Beanstalk tool behavior
#-----------------------------------------------------------------------------------------------------------------------
VERBOSE = 3
ALLOW_INSTALL_YUM_PACKAGES = True

# Beanstalk Installation
#-----------------------------------------------------------------------------------------------------------------------
BEANSTALK_STACK_BASE = '/var/beanstalk'
STATIC_URL_PREFIX = 'static'
BEANSTALK_EMAIL = 'beanstalk@beanstalk-stack.com'
UWSGI_COMMAND = '/usr/local/bin/uwsgi'
RUN_LOCATION = '/var/run/beanstalk'

# Hooked Actions
#-----------------------------------------------------------------------------------------------------------------------
PRE_SETUP_ACTIONS = []  # Only beanstalk settings
POST_SETUP_ACTIONS = []  # Only beanstalk settings

PRE_CREATE_ACTIONS = []  # project_name
POST_CREATE_ACTIONS = [
    create_database,
]  # project_name, uwsgi_port

PRE_COMMIT_ACTIONS = []  # project_name
POST_COMMIT_ACTIONS = []  # project_name

PRE_RELOAD_ACTIONS = []  # project_name
POST_RELOAD_ACTIONS = []  # project_name

PRE_INSTALL_ACTIONS = [
    install_yum_packages,
    install_pip_requirements,
    compile_python_code
]  # project_name
POST_INSTALL_ACTIONS = []  # project_name

PRE_COMMIT_ACTION = []  # project_name
POST_COMMIT_ACTION = []  # project_name

PRE_DELETE_ACTION = []  # project_name
POST_DELETE_ACTION = []  # project_name

PRE_ACTIVATE_ACTION = []  # project_name
POST_ACTIVATE_ACTION = []  # project_name

PRE_DEACTIVATE_ACTION = []  # project_name
POST_DEACTIVATE_ACTION = [
    create_venv,
    initialize_git,
]  # project_name

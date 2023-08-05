import os

# Load settings
#-----------------------------------------------------------------------------------------------------------------------
BEANSTALK_GLOBAL_BASE_PATH = '/etc/beanstalk_stack'
BEANSTALK_GLOBAL_SETTINGS_PATH = os.path.join(BEANSTALK_GLOBAL_BASE_PATH, 'beanstalk_settings.py')

# Pacakge information
#-----------------------------------------------------------------------------------------------------------------------
__version__ = '0.1.36'
VERSION = tuple(map(lambda x: int(x), __version__.split('.')))
BEANSTALK_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

# Values
#-----------------------------------------------------------------------------------------------------------------------
IDENTIFIER = 'com.wantoto.beanstalk'
BEANSTALK_LOCAL_BASE_PATH = 'bsbean/'

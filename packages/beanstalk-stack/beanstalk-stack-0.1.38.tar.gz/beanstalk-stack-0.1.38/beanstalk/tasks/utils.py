import os
from fabric.api import *
from fabric.state import output as output_level
from ground_soil.datastucture import SettingsDict
from beanstalk import (BEANSTALK_ROOT_PATH, BEANSTALK_GLOBAL_BASE_PATH,
                       BEANSTALK_LOCAL_BASE_PATH)
from beanstalk.titles import section_title


def load_role_settings(role=None, local_settings_path=None, load_again=False, default_only=False, **setting_patches):
    """Load beanstalk settings in
    """
    env_key = 'beanstalk_settings' if not default_only else 'beanstalk_default_settings'
    if not load_again and env_key in env:
        return env[env_key]

    # Check role
    if role is None:
        role = env.get('beanstalk_role', None)
    if role not in ('app', 'server'):
        abort('I don\'t know this role. ({role})'.format(role=role))

    # Get default settings path
    setting_paths = []
    default_settings_path = os.path.join(BEANSTALK_ROOT_PATH, 'default_settings/default_{0}_settings.py'.format(role))
    setting_paths.append(default_settings_path)
    # Get global role settings path
    global_settings_path = os.path.join(BEANSTALK_GLOBAL_BASE_PATH, '{0}_settings.py'.format(role))
    if os.path.exists(global_settings_path):
        setting_paths.append(global_settings_path)
    # Get local role settings path
    if not default_only:
        if local_settings_path is None:
            local_settings_path = env.get(
                'beanstalk_{0}_settings_path'.format(role),
                os.path.join(
                    os.getcwd(), BEANSTALK_LOCAL_BASE_PATH, 'beanstalk_{0}_settings.py'.format(role)
                ))
        if os.path.exists(local_settings_path):
            setting_paths.append(local_settings_path)

    beanstalk_settings = SettingsDict(*setting_paths, **setting_patches)

    env[env_key] = beanstalk_settings
    return beanstalk_settings


def set_verbose_level(verbose_level=None):
    if verbose_level is None:
        beanstalk_settings = env.get('beanstalk_settings', None)
        if beanstalk_settings is None:
            abort('Give verbose_level or Load beanstalk settings first')
        verbose_level = beanstalk_settings['VERBOSE']

    # Check output level
    if verbose_level == 0:
        hide_output_status = ['everything']
    elif verbose_level == 1:
        hide_output_status = ['status', 'stdout', 'stderr', 'running']
    elif verbose_level == 2:
        hide_output_status = ['status', 'running']
    else:
        hide_output_status = []

    for status in hide_output_status:
        setattr(output_level, status, False)

    env.verbose_level = verbose_level


def load_web_servers():
    beanstalk_settings = env.get('beanstalk_settings', None)
    if beanstalk_settings is None:
        abort('Load beanstalk settings first')

    with hide('everything'):
        execute('app.web_server', *beanstalk_settings['WEB_SERVERS'])
        if beanstalk_settings['VERBOSE'] != 0:
            puts('')

    if len(env.roledefs['web_servers']) == 0:
        abort('Where do you want to deploy to?')


def run_hooked_actions(action_name):
    beanstalk_settings = env.get('beanstalk_settings', None)
    if beanstalk_settings is None:
        abort('Load beanstalk settings first')

    actions = beanstalk_settings[action_name]
    if len(actions) != 0:
        print section_title('Run {0}-{1} {2}'.format(*action_name.lower().split('_')))
        for action in actions:
            if isinstance(action, (list, tuple)):
                action, action_args, action_kwargs = action
            else:
                action_args = []
                action_kwargs = {}
            with hide('status'):
                execute(action, *action_args, **action_kwargs)
        return True
    else:
        return False

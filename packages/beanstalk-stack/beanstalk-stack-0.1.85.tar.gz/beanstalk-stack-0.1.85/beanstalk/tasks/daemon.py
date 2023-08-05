import os
import sys
from fabric.api import *
from fabric.colors import *
from beanstalk import BEANSTALK_GLOBAL_BASE_PATH
from beanstalk.decorators import beanstalk_task
from beanstalk.tasks.utils import load_role_settings

_screen_width = 67


def _result(success, hint):
    spaces = (_screen_width - len(hint) - 8)
    status = green('  OK  ') if success else red('FALIED')
    return ' ' * spaces + '[{status}]'.format(status=status)


@beanstalk_task(beanstalk_role='server')
@with_settings(hide('running', 'status'))
def start():
    """Start the uwsgi as a daemon
    """
    hint = 'Start beanstalk:'
    sys.stdout.write(hint)

    beanstalk_settings = load_role_settings()

    pid_file = os.path.join(beanstalk_settings['RUN_LOCATION'], 'uwsgi.pid')

    arg_context = {
        'config_file': os.path.join(BEANSTALK_GLOBAL_BASE_PATH, 'uwsgi.ini'),
        'pid_file': pid_file,
    }
    command_context = {
        'command': beanstalk_settings['UWSGI_COMMAND'],
        'args': '--ini {config_file} --log-syslog=uwsgi --pidfile={pid_file}'.format(**arg_context),
    }

    if not os.path.exists(pid_file):
        with lcd(beanstalk_settings['BEANSTALK_STACK_BASE']):
            result = local('{command} {args} 1>/dev/null 2>&1'.format(**command_context))
        sys.stdout.write(_result(result.succeeded, hint))
    else:
        sys.stdout.write(_result(False, hint))
        sys.stdout.write('\nBeanstalk-stack has been already started.')

    sys.stdout.write('\n')


@beanstalk_task(beanstalk_role='server')
@with_settings(hide('running', 'status'))
def stop():
    """Stop the uwsgi daemon
    """
    hint = 'Stop beanstalk:'
    sys.stdout.write(hint)

    beanstalk_settings = load_role_settings()

    pid_file = os.path.join(beanstalk_settings['RUN_LOCATION'], 'uwsgi.pid')

    command_context = {
        'command': beanstalk_settings['UWSGI_COMMAND'],
        'args': '--stop {pid_file}'.format(pid_file=pid_file),
    }

    if not os.path.exists(pid_file):
        sys.stdout.write(_result(False, hint))
        sys.stdout.write('\nBeanstalk-stack has been already stopped.')
    else:
        result = local('{command} {args} 1>/dev/null 2>&1'.format(**command_context))
        if result.succeeded:
            local('rm -rf {pid_file}'.format(pid_file=pid_file))
        sys.stdout.write(_result(result.succeeded, hint))

    sys.stdout.write('\n')


@beanstalk_task(beanstalk_role='server')
@with_settings(hide('running', 'status'))
def reload():
    """Reload the uwsgi daemon
    """
    hint = 'Reload beanstalk:'
    sys.stdout.write(hint)

    beanstalk_settings = load_role_settings()

    pid_file = os.path.join(beanstalk_settings['RUN_LOCATION'], 'uwsgi.pid')

    command_context = {
        'command': beanstalk_settings['UWSGI_COMMAND'],
        'args': '--reload {pid_file}'.format(pid_file=pid_file),
    }

    if os.path.exists(pid_file):
        result = local('{command} {args} 1>/dev/null 2>&1'.format(**command_context))
        sys.stdout.write(_result(result.succeeded, hint))

    sys.stdout.write('\n')


@beanstalk_task(beanstalk_role='server')
@with_settings(hide('running', 'status'))
def restart():
    """Restart the uwsgi daemon
    """
    print 'Restarting beanstalk-stack:'
    with settings(hide('warnings', 'status', 'running'), warn_only=True):
        execute(stop)
        execute(start)

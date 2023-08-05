import os
from fabric.api import *
from fabric.colors import *
from fabric.contrib.files import append
from soil.filesystem import temporary_directory
from beanstalk import IDENTIFIER
from beanstalk.titles import tool_title
from beanstalk.tasks.utils import load_role_settings as load_beanstalk_settings, load_web_servers
from beanstalk.decorators import beanstalk_role
from beanstalk.validator import validate_file_existence


@task
@beanstalk_role('app')
def add(settings_path=None, **settings_patches):
    """Add current user to beanstalk-stack server
    """
    # Load settings
    load_beanstalk_settings(local_settings_path=settings_path, **settings_patches)
    load_web_servers()
    ssh_authorized_keys_path = '~/.ssh/authorized_keys'

    print tool_title('Beanstalk-Stack users tool')
    print ''

    # Get ssh public key
    ssh_pub_key_path = prompt('Where\'s your ssh public key?', default='~/.ssh/id_rsa.pub',
                              validate=validate_file_existence)
    with open(ssh_pub_key_path, 'r') as f:
        ssh_pub_key = f.read().strip()

    @roles('web_servers')
    def add_user_core():
        host_name = env.host_string.split('@')[-1]

        with temporary_directory(identifier=IDENTIFIER, prefix='add_user~') as tmp_directory:
            # Get remote authorized_keys
            local_authorized_keys_path = os.path.join(tmp_directory, 'authorized_keys')
            with hide('everything'):
                get(ssh_authorized_keys_path, local_authorized_keys_path)
            with open(local_authorized_keys_path, 'r') as local_authorized_keys:
                for authorized_key in local_authorized_keys:
                    if authorized_key.strip() == ssh_pub_key:
                        print cyan('You have been in %s.' % host_name)
                        return
            append(ssh_authorized_keys_path, ssh_pub_key)
            print green('You have joined %s.' % host_name)

    with settings(hide('running')):
        execute(add_user_core)

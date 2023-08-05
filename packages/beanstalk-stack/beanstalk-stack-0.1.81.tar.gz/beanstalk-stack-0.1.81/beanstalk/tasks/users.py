import hashlib
from fabric.api import *
from ground_soil.filesystem import rsync
from beanstalk.decorators import beanstalk_task
from beanstalk.tasks.utils import load_role_settings, load_web_servers
from beanstalk.console.titles import tool_title
from beanstalk.validator import validate_file_existence


@beanstalk_task(beanstalk_role='app')
def add(settings_path=None, **settings_patches):
    """Add current user to beanstalk-stack server
    """
    # Load settings
    load_role_settings(additional_settings_path=settings_path, **settings_patches)
    load_web_servers()

    print tool_title('Beanstalk-Stack users tool')
    print ''

    # Get ssh public key
    ssh_pub_key_path = prompt('Where\'s your ssh public key?', default='~/.ssh/id_rsa.pub',
                              validate=validate_file_existence)
    with open(ssh_pub_key_path, 'r') as f:
        key_content = f.read().strip()
    hash_key = hashlib.md5(key_content).hexdigest()[:16]
    tmp_path = '/tmp/beanstalk-stack.{hash}.pub.key'.format(hash=hash_key)

    @roles('web_servers')
    def add_user_core():
        host_name = env.host_string.split('@')[-1]

        local(rsync(ssh_pub_key_path, 'beanstalk@{host}:{key_path}'.format(host=host_name, key_path=tmp_path)))
        run('bsjack server.add_user:{key_path},clean_tmp_key=True'.format(key_path=tmp_path))

    with settings(hide('running')):
        # TODO: Should not prompt beanstalk's SSH password
        execute(add_user_core)

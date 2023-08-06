from fabric.state import env
from fabric.tasks import WrappedCallableTask


class BeanstalkTask(WrappedCallableTask):
    def __init__(self, func, *args, **kwargs):
        self.local_env = {
            'user': 'beanstalk',  # Override the value from fabricrc or other command line options
        }
        # shortcut for settiing beanstalk_role for settings
        if kwargs.get('beanstalk_role', None):
            self.local_env['beanstalk_role'] = kwargs.pop('beanstalk_role', None)
        super(BeanstalkTask, self).__init__(func, *args, **kwargs)

    def run(self, *args, **kwargs):
        # Update env
        env.update(self.local_env)
        # Run
        return super(BeanstalkTask, self).run(*args, **kwargs)

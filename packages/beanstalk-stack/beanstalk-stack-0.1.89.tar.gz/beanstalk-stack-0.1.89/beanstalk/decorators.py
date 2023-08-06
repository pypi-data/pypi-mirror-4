from functools import wraps
from fabric.api import env, task
from beanstalk.tasks.base_class import BeanstalkTask


def beanstalk_role(role):
    def wrapper(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            env.beanstalk_role = role
            return fn(*args, **kwargs)
        return wrapped
    return wrapper


def beanstalk_task(*dec_args, **dec_kwargs):
    # INVOKED: This decorator is used with "()"
    invoked = bool(not dec_args or dec_kwargs)

    if invoked:
        # If invoked, func is not passed as the first argument of this decorator
        return task(task_class=BeanstalkTask, *dec_args, **dec_kwargs)
    else:
        # If not invoked, func is passed as the first argument of this decorator
        return task(task_class=BeanstalkTask)(dec_args[0])

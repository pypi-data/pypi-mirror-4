from functools import wraps
from fabric.api import env


def beanstalk_role(role):
    def wrapper(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            env.beanstalk_role = role
            return fn(*args, **kwargs)
        return wrapped
    return wrapper

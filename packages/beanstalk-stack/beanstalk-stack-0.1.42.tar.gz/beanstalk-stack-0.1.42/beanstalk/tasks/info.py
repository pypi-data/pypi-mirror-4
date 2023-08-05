import json
from fabric.api import *
from ground_soil.fabric import eval_kwargs


@task
def version(**kwargs):
    """Get version of beanstalk-stack
    """
    import beanstalk
    kwargs = eval_kwargs(kwargs)

    use_json = kwargs.get('USE_JSON', False)

    if use_json:
        print json.dumps({
            'string': beanstalk.__version__,
            'list': beanstalk.VERSION,
        })
    else:
        print 'Beanstalk-Stack version {0}'.format(beanstalk.__version__)

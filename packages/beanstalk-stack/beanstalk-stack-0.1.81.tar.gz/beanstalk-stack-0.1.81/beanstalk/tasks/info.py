import json
from ground_soil.fabric import eval_kwargs
from beanstalk import __version__ as version_str, VERSION as version_list
from beanstalk.decorators import beanstalk_task


@beanstalk_task
def version(**kwargs):
    """Get version of beanstalk-stack
    """
    kwargs = eval_kwargs(kwargs)

    use_json = kwargs.get('USE_JSON', False)

    if use_json:
        print json.dumps({
            'string': version_str,
            'list': version_list,
        })
    else:
        print 'Beanstalk-Stack version {0}'.format(version_str)

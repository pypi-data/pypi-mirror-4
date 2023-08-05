import os
from fabric.api import *
from fabric.colors import *
from beanstalk.decorators import beanstalk_role
from beanstalk.titles import action_title


@task
@beanstalk_role('app')
def check_comments(beanstalk_settings=None):
    if beanstalk_settings is None:
        beanstalk_settings = env.get('beanstalk_settings')
    if beanstalk_settings is None:
        abort('Load beanstalk settings first')

    project_source_root = beanstalk_settings['PROJECT_SOURCE_ROOT']

    if beanstalk_settings['CHECK_COMMENTS']:
        print action_title('Check comment in source code')
        check_todo = beanstalk_settings['CHECK_TODO']
        check_note = beanstalk_settings['CHECK_NOTE']
        check_fix_me = beanstalk_settings['CHECK_FIX_ME']
        comment_types = []
        if check_todo:
            comment_types.append('TODO')
        if check_note:
            comment_types.append('NOTE')
        if check_fix_me:
            comment_types.append('FIXME')
        grep_commands = []
        comment_styles = [
            ('# %s:', ['py']),
            ('<!-- %s:', ['html']),
            ('// %s:', ['less', 'js']),
            ('/\* %s:', ['css']),
        ]
        for comment_type in comment_types:
            for comment_style, file_types in comment_styles:
                for file_type in file_types:
                    comment_string = comment_style % comment_type
                    grep_commands.append(
                        "grep '%s' -n -r %s --include=*.%s" % (comment_string, project_source_root, file_type)
                    )
        comment_search_results = []
        for grep_command in grep_commands:
            local_results = []
            with settings(hide('everything'), warn_only=True):
                result = local(grep_command, capture=True)
                if len(result):
                    local_results.append(result)
            for raw_result in local_results:
                result_components = raw_result.split(':')
                path = os.path.relpath(result_components[0], project_source_root)
                line_number = result_components[1]
                content = ':'.join(result_components[2:]).strip()
                comment_search_results.append((path, line_number, content))
        for path, line_number, content in comment_search_results:
            print 'Line %s at %s: %s' % (yellow(line_number), yellow(path, bold=True), content)
        if len(comment_search_results) == 0 and beanstalk_settings['VERBOSE'] != 0:
            print 'No comment mentioned about %s' % comment_types
        print ''

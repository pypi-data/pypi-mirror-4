import ast
import os


def required_input(value, msg=None):
    if len(value) == 0:
        raise ValueError(msg or 'You must enter someting.')


def validate_web_server(raw_value):
    required_input(raw_value, 'You must enter a Python list/tuple.')

    try:
        web_servers = ast.literal_eval(raw_value)
    except SyntaxError:
        raise ValueError('Invalid Python syntax')

    if not isinstance(web_servers, (list, tuple)):
        raise TypeError('You should input a list or a tuple')

    def element_check(e):
        if not isinstance(e, (str, unicode)):
            raise TypeError('Each element should be a string/unicode.')
    map(element_check, web_servers)

    return raw_value


def validate_file_existence(raw_value):
    required_input(raw_value, 'You must enter a path.')

    path = os.path.abspath(os.path.join(os.getcwd(), os.path.expanduser(raw_value)))
    if not os.path.exists(path):
        raise ValueError('There\'s no such file at this path.')

    return os.path.normpath(os.path.expanduser(raw_value))


def validate_project_type(raw_value):
    if raw_value.lower() in ('plain',) + supported_projects:
        return raw_value.lower()
    raise ValueError('\'{type}\' is not a supported project type. Use \'plain\' for other project'.format(
        type=raw_value))
supported_projects = ('django',)

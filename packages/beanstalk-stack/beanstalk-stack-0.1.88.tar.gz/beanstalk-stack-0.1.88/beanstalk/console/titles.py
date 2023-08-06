from fabric.api import *
from fabric.colors import *


def section_title(title):
    return title if env.get('verbose_level', 0) == 0 else cyan(title)


def tool_title(title):
    return magenta(title, bold=True)


def action_title(title):
    title = '+ {title}'.format(title=title)
    return title if env.get('verbose_level', 0) == 0 else blue(title)


def separator(char='-', screen_width=80):
    return char * int(screen_width / len(char))

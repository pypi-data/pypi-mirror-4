from fabric.api import *


def create_database(db_name=None, db_user=None, db_password=None, permissions=None):
    pass
    # TODO: Create database
#    if permissions is None:
#        permissions = env.get(
#            'db_permissions',
#            ['SELECT', 'UPDATE', 'INSERT', 'DELETE', 'INDEX', 'CREATE', 'DROP', 'ALTER', 'REFERENCES'])
#    if db_name is None:
#        db_name = env.db_name
#    if db_user is None:
#        db_user = env.db_user
#    if db_password is None:
#        db_password = env.db_password
#
#    db_info = {
#        'db_name': db_name,
#        'db_user': db_user,
#        'db_password': db_password,
#        'db_perms': ', '.join(permissions),
#    }
#
#    sql_commands = [
#        'CREATE DATABASE IF NOT EXISTS {db_name}',
#        'GRANT {db_perms} ON {db_name}.* TO {db_user}@\'localhost\' IDENTIFIED BY \'{db_password}\'',
#        'FLUSH PRIVILEGES',
#    ]
#
#    for sql_command in sql_commands:
#        print sql_command.format(**db_info)

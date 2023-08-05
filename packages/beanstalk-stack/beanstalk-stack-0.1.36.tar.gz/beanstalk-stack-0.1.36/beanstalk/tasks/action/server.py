

def create_database(db_name, db_user, db_password, permissions=None):
    if permissions is None:
        permissions = ['SELECT', 'UPDATE', 'INSERT', 'DELETE', 'INDEX', 'CREATE', 'DROP', 'ALTER', 'REFERENCES']

    db_info = {
        'db_name': db_name,
        'db_user': db_user,
        'db_password': db_password,
        'db_perms': ', '.join(permissions),
    }

    sql_commands = [
        'CREATE DATABASE IF NOT EXISTS {db_name}',
        'GRANT {db_perms} ON {db_name}.* TO {db_user}@\'localhost\' IDENTIFIED BY \'{db_password}\'',
        'FLUSH PRIVILEGES',
    ]

    for sql_command in sql_commands:
        print sql_command.format(**db_info)

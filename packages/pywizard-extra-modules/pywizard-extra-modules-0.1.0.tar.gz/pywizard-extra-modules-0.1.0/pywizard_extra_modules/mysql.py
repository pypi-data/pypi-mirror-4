from pywizard.resources.file import file_
from pywizard.resources.package import package
from pywizard.resources.python import PythonResource
from pywizard.resources.service import service
from pywizard.resources.shell import shell
from pywizard.utils.process import run
from pywizard.worker import worker


def mysql_execute(sql, user, password):
    return run("echo '%s' | mysql -u%s -p%s" % (sql, user, password))


def get_root_passwd():
    with open('/root/.mysql_password', 'r') as f:
        root_passwd = f.read()
    return root_passwd


def mysql_database(user, password, db_name=None):

    if not db_name:
        db_name = user

    def database_exist():
        root_password = get_root_passwd()
        return "\n%s\n" % db_name in mysql_execute('show databases', 'root', root_password)

    def _apply():
        root_password = get_root_passwd()
        mysql_execute("""GRANT ALL privileges ON %s.* TO %s@localhost IDENTIFIED BY "%s"; FLUSH PRIVILEGES;""" %
                      (user, user, password), 'root', root_password)
        params = 'DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci'
        mysql_execute('CREATE DATABASE %s %s;' % (user, params), 'root', root_password)

    def _rollback():
        root_password = get_root_passwd()
        mysql_execute("DROP USER %s;FLUSH PRIVILEGES;" % user, 'root', root_password)
        mysql_execute('DROP DATABASE %s;' % user, 'root', root_password)

    worker.register_resource(
        PythonResource(
            _apply,
            _rollback,
            if_not=database_exist
        )
    )


def mysql_server(root_password):

    file_('/root/.mysql_password', content=root_password)

    def init_root_password():
        run('echo mysql-server mysql-server/root_password password %s | sudo debconf-set-selections' % root_password)
        run('echo mysql-server mysql-server/root_password_again password %s | sudo debconf-set-selections' % root_password)

    package('mysql-server', before_install=init_root_password)
    service('mysql')
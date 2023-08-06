from pywizard.facts import is_centos
from pywizard.resources.file import file_
from pywizard.resources.package import package
from pywizard.resources.service import service
from pywizard.templating import tpl


def php_fpm(host, port):

    if is_centos():
        www_conf = '/etc/php-fpm.d/www.conf'

        package([
            'php',
            'php-fpm',
        ])

        php_fpm_service = service('php-fpm')

    else:
        www_conf = '/etc/php5/fpm/pool.d/www.conf'

        package([
            'php5',
            'php5-fpm',
        ])

        php_fpm_service = service('php5-fpm')

    file_(
        www_conf,
        content=tpl('php-fpm.conf', context=locals()),
        on_create=(
            php_fpm_service.start,
        ),
        on_update=(
            php_fpm_service.reload,
        ),
        if_exist=(
            php_fpm_service.start,
        ),
    )




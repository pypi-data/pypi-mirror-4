from pywizard.resources.file import file_
from pywizard.resources.package import package
from pywizard.resources.service import service
from pywizard.templating import tpl


def php_fpm(host, port):

    package([
        'php5',
        'php5-fpm',
    ])

    php_fpm_service = service('php5-fpm')

    file_(
        '/etc/php5/fpm/pool.d/www.conf',
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




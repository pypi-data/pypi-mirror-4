from pywizard.resources.file import file_
from pywizard.resources.package import package
from pywizard.resources.service import service
from pywizard.templating import tpl
from pywizard_extra_modules.utils import replace_in_file


def stunnel(ssl_cert, ssl_key, source, dest):
    package('stunnel4')

    replace_in_file('/etc/default/stunnel4', 'ENABLED=0', 'ENABLED=1')

    stunnel_service = service('stunnel4', start=False)

    file_(
        '/etc/stunnel/main.conf',
        content=tpl('stunnel.conf', context=locals()),
        on_create=(
            stunnel_service.start,
        ),
        on_update=(
            stunnel_service.reload,
        ),
        if_exist=(
            stunnel_service.start,
        ),
    )



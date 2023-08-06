from pywizard.resources.file import file_
from pywizard.resources.package import package
from pywizard.resources.service import service
from pywizard.templating import tpl


def varnish_nodejs_filter(host, port, node_urls):

    package('varnish')

    varnish_service = service('varnish', start=False, process_name='varnishd')

    file_(
        '/etc/default/varnish',
        content=tpl('varnish-default', context=locals()),
        on_update=(
            varnish_service.restart,
        )
    )
    file_(
        '/etc/varnish/default.vcl',
        content=tpl('default.vcl', context=locals()),
        on_update=(
            varnish_service.reload,
        )
    )
    file_(
        '/etc/varnish/sites.vcl',
        content=tpl('sites.vcl', context=locals()),
        on_create=(
            varnish_service.start,
        ),
        on_update=(
            varnish_service.reload,
        ),
        if_exist=(
            varnish_service.start,
        ),
    )

    return varnish_service


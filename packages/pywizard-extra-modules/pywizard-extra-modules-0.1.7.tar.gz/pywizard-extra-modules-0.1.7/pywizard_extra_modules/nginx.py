
from pywizard.resources.file import file_
from pywizard.resources.package import package
from pywizard.resources.service import service
from pywizard.templating import tpl
from pywizard.utils.resources import aggregate_config


def nginx(
        name,
        domain_name,
        host,
        port,
        root_directory,
        template=None,
        fastcgi_pass=None,
        assets_path=None,
        assets_dirs=None
):
    config = aggregate_config(nginx, '%s' % name, locals())

    package('nginx-full')

    nginx_service = service('nginx', start=False)

    # remove default config
    file_('/etc/nginx/sites-enabled/default', content='')

    for name, data in config.iteritems():
        file_(
            '/etc/nginx/sites-enabled/%s.conf' % name,
            content=tpl(template, context=data),
            on_create=(
                nginx_service.restart,
            ),
            on_update=(
                nginx_service.restart,
            ),
            if_exist=(
                nginx_service.start,
            ),
        )

    return nginx_service





# def nginx(host_name, port, root_directory):
#     package('nginx')
#
#     # with wiz
#     # with notify(reload_nginx):
#     file_(
#         '/etc/nginx/conf.d/test1',
#         content=from_template('nginx.conf', {
#             'domain': host_name,
#             'port': port,
#             'root': root_directory
#         }),
#         )
#
#     #service('nginx')
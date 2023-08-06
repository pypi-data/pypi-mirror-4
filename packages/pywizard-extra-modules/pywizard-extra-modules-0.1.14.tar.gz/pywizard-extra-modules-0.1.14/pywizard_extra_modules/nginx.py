from pywizard.facts import is_ubuntu, is_centos, distro
from pywizard.resources.file import file_, directory
from pywizard.resources.package import package
from pywizard.resources.service import service
from pywizard.resources.shell import shell
from pywizard.resources.user import user
from pywizard.templating import tpl
from pywizard.utils.process import run
from pywizard.utils.resources import aggregate_config


def nginx_dev(version, user='nginx'):

    if is_ubuntu():
        package('make libc6 libpcre3 libpcre3-dev libpcrecpp0 libssl0.9.8 libssl-dev zlib1g zlib1g-dev lsb-base'.split(' '))
    if is_centos():
        package('pcre pcre-devel zlib zlib-devel openssl openssl-devel'.split(' '))

    def nginx_installed():
        return version in str(run('nginx -v  2>&1', ignore_errors=True))

    shell(tpl('install_nginx.sh', locals()), if_not=nginx_installed)

    directory('/etc/nginx/conf.d')
    file_('/etc/nginx/nginx.conf', content=tpl('nginx-main.conf'))

    def set_rights():
        run('chmod +x /etc/init.d/nginx')
    file_('/etc/init.d/nginx', tpl('nginx-init-%s' % distro()), on_create=set_rights)


def nginx(
        name,
        template=None,
        **kwargs
):
    if not kwargs:
        kwargs = {}
    kwargs['name'] = name

    config = aggregate_config(nginx, '%s' % name, kwargs)

    user('nginx')

    nginx_dev('1.3.15', user='nginx')
    #package('nginx-full')

    nginx_service = service('nginx', start=False)

    # remove default config
    # file_('/etc/nginx/sites-enabled/default', content='')

    for name, data in config.iteritems():
        file_(
            '/etc/nginx/conf.d/%s.conf' % name,
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
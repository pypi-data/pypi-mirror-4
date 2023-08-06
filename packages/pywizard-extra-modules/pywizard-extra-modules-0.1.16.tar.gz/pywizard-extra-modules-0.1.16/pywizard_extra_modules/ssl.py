import os
from pywizard.resources.file import directory, file_
from pywizard.resources.shell import shell
from pywizard.templating import tpl
from pywizard.worker import worker


def ssl_fake_cert(
        path,
        keyname='fake.key',
        csrname='fake.csr',
        crtname='fake.crt',
):
    def certs_are_here():
        return os.path.exists(path + '/' + keyname) and \
            os.path.exists(path + '/' + csrname) and os.path.exists(path + '/' + crtname)

    directory(path)

    file_(path + '/ssl.conf', content=tpl('ssl.conf', locals()))
    shell(tpl('fake_ssl_script.sh', locals()), if_not=certs_are_here)

    template_engine = worker.env.get_template_engine()

    template_engine.globals['ssl_key_path'] = path + '/' + keyname
    template_engine.globals['ssl_cert_path'] = path + '/' + crtname

from pywizard.resources.package import package
from pywizard.resources.shell import shell
from pywizard.templating import tpl
from pywizard.utils.process import run


def nodejs(version):

    package('make')

    def node_is_installed():
        return run('node -v', ignore_errors=True) == 'v' + version

    shell(tpl('install-nodejs.sh', locals()), if_not=node_is_installed)
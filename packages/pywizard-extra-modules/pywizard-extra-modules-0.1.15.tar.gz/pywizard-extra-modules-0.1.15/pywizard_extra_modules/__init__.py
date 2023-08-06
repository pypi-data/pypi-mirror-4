from jinja2.loaders import PackageLoader
from pywizard.worker import worker

worker.env.template_loaders.append(
    PackageLoader(__name__)
)
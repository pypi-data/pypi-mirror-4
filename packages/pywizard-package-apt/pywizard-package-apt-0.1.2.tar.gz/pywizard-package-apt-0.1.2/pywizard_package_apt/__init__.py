from pywizard.resources.package import package
from pywizard.worker import worker


def install_libs():
    package('libapt-pkg-dev')

worker.env.requirements.append(install_libs)
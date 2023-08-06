from pywizard.resources.package import package, register_package_provider
from pywizard.worker import worker
from pywizard_package_apt.package_provider import AptPackageProvider


def install_libs():
    package('libapt-pkg-dev')

worker.env.requirements.append(install_libs)

register_package_provider(AptPackageProvider)
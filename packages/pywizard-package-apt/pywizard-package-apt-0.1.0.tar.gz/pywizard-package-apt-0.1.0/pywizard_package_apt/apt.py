from pywizard.resources.package import PackageProvider, register_package_provider
import apt


class AptPackageProvider(PackageProvider):

    @staticmethod
    def get_key():
        return 'apt'

    def can_install_system_packages(self):
        return True

    def install_packages(self, packages, version=None):
        cache = apt.Cache()
        for package in packages:
            cache[package].mark_install()

        cache.commit()

    def uninstall_packages(self, packages, version=None):
        cache = apt.Cache()
        for package in packages:
            cache[package].mark_delete()

        cache.commit()

    def get_installed(self, packages):

        cache = apt.Cache()
        installed = []
        for package in packages:
            if cache[package].is_installed:
                installed.append(package)

        return set(installed)


register_package_provider(AptPackageProvider)


import os
from setuptools import setup

setup(
    name='pywizard-package-apt',
    version='0.1.0',
    packages=[
        'pywizard_package_apt',
    ],
    url='',
    license='MIT',
    author='Alex Rudakov',
    author_email='ribozz@gmail.com',
    description='Apt package provider',
    long_description=open('README.md').read(),
    install_requires=[
        'pywizard',
        'python-apt',
    ]
)

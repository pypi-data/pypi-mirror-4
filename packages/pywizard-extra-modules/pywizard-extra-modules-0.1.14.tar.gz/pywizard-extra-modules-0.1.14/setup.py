import os
from setuptools import setup

setup(
    name='pywizard-extra-modules',
    version='0.1.14',
    packages=[
        'pywizard_extra_modules',
    ],
    package_data={'pywizard_extra_modules': ['templates/*']},
    url='',
    license='MIT',
    author='Alex Rudakov',
    author_email='ribozz@gmail.com',
    description='Pack of modules for Pywizard',
    long_description=open('README.md').read(),
    install_requires=[
        'pywizard>=0.2.26',
    ]
)

import os
from setuptools import setup

setup(
    name='pywizard-extra-modules',
    version='0.1.0',
    packages=[
        'pywizard_extra_modules',
    ],
    url='',
    license='MIT',
    author='Alex Rudakov',
    author_email='ribozz@gmail.com',
    description='Pack of modules for Pywizard',
    long_description=open('README.md').read(),
    install_requires=[
        'pywizard',
    ]
)

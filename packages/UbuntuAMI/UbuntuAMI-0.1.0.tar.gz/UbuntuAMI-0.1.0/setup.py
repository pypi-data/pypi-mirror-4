#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='UbuntuAMI',
    version='0.1.0',
    description='Get the daily build ami of Ubuntu Cloud Image',
    author='Lx Yu',
    author_email='lixinfish@gmail.com',
    py_modules=['ubuntuami', ],
    package_data={'': ['LICENSE'], },
    url='http://lxyu.github.com/ubuntuami/',
    license=open('LICENSE').read(),
    long_description=open('README.rst').read(),
    install_requires=[
        'cssselect',
        'lxml',
        'requests',
    ],
)

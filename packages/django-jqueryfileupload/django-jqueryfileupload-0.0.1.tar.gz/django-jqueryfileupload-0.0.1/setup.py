#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

from jqueryfileupload import __version__

version = ".".join(map(str, __version__))

setup(
    name='django-jqueryfileupload',
    version=version,
    description='Django app for handle multiple file uploads via jquery-file-upload plugin.',
    author='Pedro Buron, Alejandro Varas',
    author_email='pedro@witoi.com, alejandro@witoi.com',
    long_description=open('README.md', 'r').read(),
    url='http://desarrollo.witoi.com/',
    packages=[
        'jqueryfileupload',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
    install_requires=['Django>=1.3'],
    test_suite='run_tests.run',
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name     = 'smart_date',
    version  = '2.0.1',
    packages = find_packages(),
    requires = ['python (>= 2.5)'],
    description  = 'Interpreter string into an array of dates. A clever feature of Alexei Klimenko.',
    long_description = open('README.md').read(),
    author       = 'Valeriy Semenov',
    author_email = 'valery.ravall@gmail.com',
    url          = 'https://github.com/Ravall/smart_date.git',
    download_url = 'https://github.com/Ravall/smart_date/tarball/master',
    license      = 'MIT License',
    keywords     = '',
    classifiers  = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
)

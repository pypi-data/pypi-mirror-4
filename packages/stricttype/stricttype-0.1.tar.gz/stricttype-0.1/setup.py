#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name     = 'stricttype',
    version  = '0.1',
    packages = find_packages(),
    requires = ['python (>= 2.5)'],
    description  = 'Python type checker.',
    long_description = open('README.markdown').read(), 
    author       = 'Gennadiy Zlobin',
    author_email = 'gennad.zlobin@gmail.com',
    url          = 'https://github.com/gennad/stricttype',
    download_url = 'https://github.com/gennad/stricttype/tarball/master',
    license      = 'MIT License',
    keywords     = 'type',
    classifiers  = [
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
)

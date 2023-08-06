#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
#
#
# Copyright 2012 ShopWiki
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from setuptools import setup

VERSION = '0.0.0'
DESCRIPTION = 'Web Authentication with SQLAlchemy'

setup(
    name='Clortho',
    version=VERSION,
    description=DESCRIPTION,
    author='Patrick Lawson',
    license='Apache 2',
    author_email='plawson@shopwiki.com',
    url='http://github.com/shopwiki/clortho',
    packages=['clortho', 'clortho.tests'],
    install_requires=['sqlalchemy', 'py-bcrypt', 'pysqlite'],
    tests_require=['nose'],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

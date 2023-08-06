#!/usr/bin/env python
#This file is part of ERP DB Copy. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

import os
from setuptools import setup, find_packages

execfile(os.path.join('erpdbcopy', 'version.py'))


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name=PACKAGE,
        version=VERSION,
        author='Zikzakmedia SL',
        author_email='zikzak@zikzakmedia.com',
        url="https://www.zikzakmedia.com",
        description="ERP DB Copy",
        long_description=read('README'),
        download_url="https://bitbucket.org/zikzakmedia/python-erpdbcopy",
        packages=find_packages(),
        scripts=['bin/erpdbcopy'],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Affero General Public License v3',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Software Development :: Libraries :: Python Modules',
            ],
        license='GPL-3',
        extras_require={
        },
        # test_suite="envialia.tests",
    )

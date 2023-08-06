##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup"""

import os
from setuptools import setup, find_packages

def read(path):
    rnames = path.split('/')
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='z3c.preference',
    version='0.5',
    author = "Michael Howitz",
    author_email = "zope-dev@zope.org",
    description = "UI for zope.preference using z3c.pagelet and z3c.form.",
    long_description='\n\n'.join([
            read('README.txt'),
            '.. contents::',
            read('CHANGES.txt'),
            read('src/z3c/preference/README.txt'),
            read('src/z3c/preference/categories.txt'),
            read('TODO.txt'),
        ]),
    license = "ZPL 2.1",
    keywords = "zope3 bluebream z3c preference ui",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'
        ],
    url = 'http://pypi.python.org/pypi/z3c.preference',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = [
            'zope.app.wsgi >= 3.7',
            'zope.browserresource',
            'zope.login',
            'zope.principalregistry',
            'zope.app.principalannotation',
            'zope.securitypolicy',
            'zope.testbrowser',
            'zope.testing',
            ],
        ),
    install_requires = [
        'setuptools',
        'z3c.form',
        'z3c.formui',
        'z3c.pagelet',
        'zope.preference',
        ],
    zip_safe = False,
)

##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id$
"""

import os
import sys
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

def test_suite():
    # use the zope.testrunner machinery to find all the
    # test suites we've put under ourselves
    from zope.testrunner.options import get_options
    from zope.testrunner.find import find_suites
    from unittest import TestSuite
    here = os.path.abspath(os.path.dirname(sys.argv[0]))
    args = sys.argv[:]
    src = os.path.join(here, 'src')
    defaults = ['--test-path', src]
    options = get_options(args, defaults)
    suites = list(find_suites(options))
    return TestSuite(suites)


setup(
    name = 'z3c.configurator',
    version='2.0.0a1',
    author = "Zope Community",
    author_email = "zope-dev@zope.org",
    description = "Dynamic configuration",
    long_description=(
        read('README.txt')
        + '\n\n.. contents::\n\n' +
        read('src', 'z3c', 'configurator', 'README.txt')
        + '\n\n' +
        read('src', 'z3c', 'configurator', 'browser', 'README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = 'ZPL 2.1',
    keywords = 'zope3 z3c configurator configuration',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.python.org/pypi/z3c.configurator',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = [
            'zope.testing',
            ],
        ftest = [
            'zope.annotation',
            'zope.dublincore',
            'zope.formlib',
            'zope.securitypolicy',
            'zope.testbrowser',
            'zope.app.pagetemplate',
            'zope.app.testing',
            'zope.app.zcmlfiles',
            ],
        zmi = [
            'zope.browserpage',
            'zope.formlib',
            ],
        ),
    test_suite='__main__.test_suite',
    install_requires = [
        'setuptools',
        'zope.component',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.schema',
        ],
    zip_safe=False,
    )

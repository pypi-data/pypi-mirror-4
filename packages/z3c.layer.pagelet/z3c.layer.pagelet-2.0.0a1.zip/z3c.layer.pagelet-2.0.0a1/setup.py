##############################################################################
#
# Copyright (c) 2007-2009 Zope Foundation and Contributors.
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

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

def alltests():
    import os
    import sys
    import unittest
    # use the zope.testrunner machinery to find all the
    # test suites we've put under ourselves
    import zope.testrunner.find
    import zope.testrunner.options
    here = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
    args = sys.argv[:]
    defaults = ["--test-path", here]
    options = zope.testrunner.options.get_options(args, defaults)
    suites = list(zope.testrunner.find.find_suites(options))
    # Filter out all tests with layers.
    import zope.testrunner.eggsupport
    suites = [zope.testrunner.eggsupport.skipLayers(suite)
              for suite in suites]
    return unittest.TestSuite(suites)

TESTS_REQUIRE = [
    'WebTest',
    'zope.app.wsgi >= 3.8',
    'zope.exceptions',
    'zope.principalregistry',
    'zope.publisher',
    'zope.security',
    'zope.securitypolicy',
    'zope.testing',
    'zope.testrunner',
]

setup(
    name='z3c.layer.pagelet',
    version='2.0.0a1',
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    description = "Pagelet layer setup for Zope 3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        '.. contents::'
        + '\n\n' +
        read('src', 'z3c', 'layer', 'pagelet', 'README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    keywords = "z3c pagelet layer zope zope3",
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
        'Programming Language :: Python :: Implementation :: CPython',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url='http://pypi.python.org/pypi/z3c.layer.pagelet',
    license='ZPL 2.1',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c', 'z3c.layer'],
    extras_require = dict(
        test = TESTS_REQUIRE,
        ),
    install_requires = [
        'setuptools',
        'z3c.pagelet',
        'z3c.template',
        'zope.authentication',
        'zope.browser>=1.2',
        'zope.browserresource',
        'zope.component',
        'zope.interface',
        'zope.login',
        'zope.publisher>=3.12',
        ],
    tests_require=TESTS_REQUIRE,
    test_suite='__main__.alltests',
    zip_safe = False,
)


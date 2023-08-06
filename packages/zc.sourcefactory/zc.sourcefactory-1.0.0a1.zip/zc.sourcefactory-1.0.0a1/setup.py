##############################################################################
#
# Copyright Zope Foundation and Contributors.
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
"""Setup
"""
from setuptools import setup, find_packages
import os.path

def read_file(*args):
    path = os.path.join(os.path.dirname(__file__), *args)
    file_contents = open(path, 'r').read()
    return file_contents + '\n\n'

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
    return unittest.TestSuite(suites)

setup(
    name='zc.sourcefactory',
    version='1.0.0a1',
    author='Zope Corporation and Contributors',
    author_email='zope-dev@zope.org',
    url='http://pypi.python.org/pypi/zc.sourcefactory',
    keywords='zope zope3 vocabulary source factory',
    description='An easy way to create custom Zope 3 sources.',
    license='ZPL 2.1',
    long_description=(
        read_file('src', 'zc', 'sourcefactory', 'README.txt') +
        read_file('src', 'zc', 'sourcefactory', 'mapping.txt') +
        read_file('src', 'zc', 'sourcefactory', 'constructors.txt') +
        read_file('src', 'zc', 'sourcefactory', 'adapters.txt') +
        read_file('src', 'zc', 'sourcefactory', 'browser', 'README.txt') +
        read_file('src', 'zc', 'sourcefactory', 'browser', 'token.txt') +
        read_file('CHANGES.txt')
        ),
    classifiers = [
        'Topic :: Software Development',
        'Framework :: Zope3',
        'Development Status :: 5 - Production/Stable',
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
        ],

    packages=find_packages('src'),
    package_dir={'':'src'},

    include_package_data=True,
    install_requires=[
        'ZODB',
        'persistent',
        'setuptools',
        'zope.intid',
        'zope.browser',
        'zope.component',
        'zope.dublincore',
        'zope.interface',
        'zope.proxy',
        'zope.publisher',
        'zope.schema',
        ],
    namespace_packages=['zc'],
    extras_require={
        'test': [
            'zope.component[zcml]',
            'zope.site',
            'zope.testing',
            'zope.testrunner',
            'zope.keyreference',
            ]},
    tests_require = [
        'zope.component[zcml]',
        'zope.keyreference',
        'zope.site',
        'zope.testing',
        'zope.testrunner',
        ],
    test_suite = '__main__.alltests',
    zip_safe=False,
    )

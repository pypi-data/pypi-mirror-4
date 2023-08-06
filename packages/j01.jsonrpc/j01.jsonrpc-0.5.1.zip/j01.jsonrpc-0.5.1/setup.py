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
"""Setup

$Id:$
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='j01.jsonrpc',
    version='0.5.1',
    author = "Roger Ineichen, Projekt01 GmbH",
    author_email = "dev@projekt01.ch",
    description = "JSON-RPC helpers based on JQuery, z3c.form and z3cjsonrpc for Zope 3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "J01 XHR ajax z3c form JSON-RPC JQuery Zope3",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.python.org/pypi/j01.jsonrpc',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['j01'],
    extras_require = dict(
        test = [
            'z3c.form[test]',
            'z3c.jsonrpc[test]',
            'z3c.macro',
            'z3c.template',
            'zope.container',
            'zope.pagetemplate',
            'zope.password',
            'zope.publisher',
            'zope.schema',
            'zope.testing',
            'zope.traversing',
            ],
        ),
    install_requires = [
        'setuptools',
        'z3c.form',
        'z3c.jsonrpc',
        'z3c.jsonrpcproxy',
        'z3c.pagelet',
        'zope.browserresource',
        'zope.component',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.location',
        'zope.publisher',
        'zope.traversing',
        'zope.viewlet',
        ],
    zip_safe = False,
    )

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

$Id: setup.py 81198 2007-10-30 08:08:29Z icemac $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='p01.locales',
    version='0.5.2',
    author = "Roger Ineichen, Projekt01 GmbH",
    author_email = "dev@projekt01.ch",
    description = "Translation for p01 package namespace",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "P01 i18n message factory Zope3",
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
    url = 'http://pypi.python.org/pypi/p01.locales',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['p01'],
    extras_require=dict(
        test=[
            'zope.testing',
            ],
        extract = [
            'j01.datepicker',
            'j01.dialog',
            #'j01.gmap', not released yet
            'j01.jsonrpc',
            'j01.rater',
            'j01.searcher',
            'j01.select2',
            'j01.selectordered',
            'j01.wizard',
            'm01.bayes',
            'm01.fs',
            'm01.grid',
            'm01.mongo',
            'm01.searcher',
            'm01.session',
            'p01.cdn',
            'p01.form',
            'p01.fsfile',
            'p01.fswidget',
            'p01.secureprincipal',
            #'p01.speedup', not released yet
            'p01.tmp',
            'p01.util',
            'p01.vocabulary.country',
            'p01.vocabulary.language',
            'p01.vocabulary.legacy',
            'p01.widget.password',
            'z3c.csvvocabulary',
            ],
        ),
    install_requires = [
        'setuptools',
        'zope.i18nmessageid',
        ],
    zip_safe = False,
    )

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

$Id: setup.py 82497 2007-12-28 14:59:22Z rogerineichen $
"""
import os
import xml.sax.saxutils
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = 'p01.recipe.cdn',
    version = '0.5.1',
    author = 'Roger Ineichen and the Zope Community',
    author_email = 'zope-dev@zope.org',
    description = 'Content delivery network Concept supporting resource offload',
    long_description=(
        read('README.txt')
        + '\n\n' +
        'Detailed Documentation\n'
        '**********************'
        + '\n\n' +
        read('src', 'p01', 'recipe', 'cdn', 'README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = 'ZPL 2.1',
    keywords = 'zope3 p01 recipe cdn content delivery network minify bundle js javascript css',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.python.org/pypi/p01.recipe.cdn',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['p01', 'p01.recipe'],
    extras_require = dict(
        test = [
            'zope.testing',
            'jsmin',
            'lpjsmin',
            'slimit',
            'cssmin',
            'argparse',
            'Pillow',
            ],
        ),
    install_requires = [
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg',
        ],
    entry_points = {
        'zc.buildout': [
             'cdn = p01.recipe.cdn.app:CDNRecipe',
             'minify = p01.recipe.cdn.app:MinifyRecipe',
             'glue = p01.recipe.cdn.app:GlueRecipe',
         ]
    },
)

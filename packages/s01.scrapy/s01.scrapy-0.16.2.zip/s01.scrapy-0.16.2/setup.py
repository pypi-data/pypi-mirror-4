###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup (
    name='s01.scrapy',
    version = '0.16.2',
    author = "Roger Ineichen, Projekt01 GmbH",
    author_email = "dev@projekt01.ch",
    description = "Package for buildout based scrapy spider development",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "scrapy s01 p01 mongodb buildout json-rpc zope zope3",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.python.org/pypi/s01.scrapy',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['s01'],
    extras_require=dict(
        test=[
            'zope.testing',
            'zc.buildout',
            'zc.recipe.egg',
             ]),
    install_requires = [
        'setuptools',
        'scrapy',
        'simplejson',
        'twisted',
        'zc.buildout',
        'zc.recipe.egg',
        'zope.interface',
        'zope.schema',
        ],
    zip_safe = False,
    entry_points = {
        'zc.buildout': [
             'scrapy = s01.scrapy.recipe:ScrapyRecipe',
             'crawl = s01.scrapy.recipe:CrawlRecipe',
             'list = s01.scrapy.recipe:ListRecipe',
             'settings = s01.scrapy.recipe:SettingsRecipe',
             'test = s01.scrapy.recipe:TestRecipe',
         ]
    },
)
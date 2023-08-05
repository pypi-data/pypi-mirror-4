##############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH and Contributors.
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


import sys
import doctest
import re
import unittest

import zc.buildout.testing

from zope.testing import renormalizing


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install('lxml', test)
    zc.buildout.testing.install_develop('s01.scrapy', test)
    zc.buildout.testing.install('Twisted', test)
    version = sys.version_info
    if version[0] == 2 and version[1] == 6:
        # only install for version python 2.6
        zc.buildout.testing.install('ordereddict', test)
    zc.buildout.testing.install('pyopenssl', test)
    zc.buildout.testing.install('scrapy', test)
    zc.buildout.testing.install('simplejson', test)
    zc.buildout.testing.install('w3lib', test)
    zc.buildout.testing.install('zc.recipe.egg', test)
    zc.buildout.testing.install('zope.event', test)
    zc.buildout.testing.install('zope.interface', test)
    zc.buildout.testing.install('zope.schema', test)
    zc.buildout.testing.install('zope.testing', test)


checker = renormalizing.RENormalizing([
    zc.buildout.testing.normalize_path,
    (re.compile(
    "Couldn't find index page for '[a-zA-Z0-9.]+' "
    "\(maybe misspelled\?\)"
    "\n"
    ), ''),
    (re.compile("""['"][^\n"']+z3c.recipe.dev[^\n"']*['"],"""),
     "'/z3c.recipe.dev',"),
    (re.compile("""['"][^\n"']+site-packages[^\n"']*['"],"""),
     "'/site-packages',"),
    (re.compile('#![^\n]+\n'), ''),
    (re.compile('-\S+-py\d[.]\d(-\S+)?.egg'),
     '-pyN.N.egg',
    ),
    (re.compile('install_dir .*'), ''),
    zc.buildout.testing.normalize_path,
    zc.buildout.testing.normalize_script,
    zc.buildout.testing.normalize_egg_py,
    ])


def test_suite():
    return unittest.TestSuite(
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE,
            checker=checker),
        )

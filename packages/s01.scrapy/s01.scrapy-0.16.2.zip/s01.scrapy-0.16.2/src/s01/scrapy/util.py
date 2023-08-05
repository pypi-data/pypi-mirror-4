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

import datetime
import os.path


# we will export the settings in cmdline and reference here 
settings = None


# file and directory handling, used for setup settings
def getNewFileName(dirPath, prefix='csv'):
    now = datetime.datetime.now()
    fName = '%s.%s' % (now.strftime("%Y%m%d-%H-%M-%S-utc"), prefix)
    return os.path.abspath(os.path.join(dirPath, fName))


def getRootDirPath(path='.', prevpath=None):
    """Return the parts/testing path from the current package based on the 
    found setup.py file
    """
    if path == prevpath:
        return ''
    path = os.path.abspath(path)
    p = os.path.join(path, 'setup.py')
    if os.path.exists(p):
        return os.path.dirname(p)
    return getRootDirPath(os.path.dirname(path), path)


def getTempDirPath():
    """Return the parts/tmp path from the current package based on the 
    found setup.py file.
    """
    root = getRootDirPath()
    if os.path.exists(root):
        return os.path.join(root, 'parts', 'tmp')
    else:
        raise ValueError(
            "tmp dir path not found in parts based on setup.py")


def getLogFileName():
    """Return the parts/log path from the current package based on the 
    found setup.py file.
    """
    root = getRootDirPath()
    if os.path.exists(root):
        dirPath = os.path.join(root, 'parts', 'log')
        return getNewFileName(dirPath, 'log')
    else:
        raise ValueError(
            "logs dir path not found in parts based on setup.py")

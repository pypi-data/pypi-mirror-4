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

import re
import time
import datetime

_marker = object()


# datetime
DATE_STRINGS = [
    # day month year
    '%d.%m.%Y',
    '%d-%m-%Y',
    # year month day
    '%Y.%m.%d',
    '%Y-%m-%d',
    ]
TIME_STRINGS = [
    '',
    '%H',
    '%H:%M',
    '%H:%M:%S',
    ]
TIMEZONE_STRINGS = [
    '',
    ]
#DATE_FORMATS = [
#    '%d.%m.%Y',
#    '%d.%m.%Y %H:%M',
#    '%d.%m.%Y %H:%M:%S',
#    '%d-%m-%Y',
#    '%d-%m-%Y %H:%M',
#    '%d-%m-%Y %H:%M:%S',
#    ]

def getDateFormats():
    for ds in DATE_STRINGS:
        for ts in TIME_STRINGS:
            for tz in TIMEZONE_STRINGS:
                dtStr = '%s %s %s' % (ds, ts, tz)
                yield dtStr.strip()

def datetimeConverter(value):
    """Convert date time strings to a datetime object"""
    if isinstance(value, basestring):
        value = value.strip()
        # only convert a basestring
        for fmt in getDateFormats():
            try:
                tt = time.strptime(value, fmt)
                ts = time.mktime(tt)
                value = datetime.datetime.fromtimestamp(ts) 
                break
            except:
                pass
    return value


# email
RFC822_SPECIALS = '()<>@,;:\\"[]'

def isValidMailAddress(addr):
    """Returns True if the email address is valid and False if not."""

    # First we validate the name portion (name@domain)
    if not addr:
        return False
    c = 0
    while c < len(addr):
        if addr[c] == '@':
            break
        # Make sure there are only ASCII characters
        if ord(addr[c]) <= 32 or ord(addr[c]) >= 127:
            return False
        # A RFC-822 address cannot contain certain ASCII characters
        if addr[c] in RFC822_SPECIALS:
            return False
        c = c + 1

    # check whether we have any input and that the name did not end with a dot
    if not c or addr[c - 1] == '.':
        return False

    # check also starting and ending dots in (name@domain)
    if addr.startswith('.') or addr.endswith('.'):
        return False

    # Next we validate the domain portion (name@domain)
    domain = c = c + 1
    # Ensure that the domain is not empty (name@)
    if domain >= len(addr):
        return False
    count = 0
    while c < len(addr):
        # Make sure that domain does not end with a dot or has two dots in a row
        if addr[c] == '.':
            if c == domain or addr[c - 1] == '.':
                return False
            count = count + 1
        # Make sure there are only ASCII characters
        if ord(addr[c]) <= 32 or ord(addr[c]) >= 127:
            return False
        # A RFC-822 address cannot contain certain ASCII characters
        if addr[c] in RFC822_SPECIALS:
            return False
        c = c + 1
    if count >= 1:
        return True
    else:
        return False

def emailConverter(value):
    """Convert anything to an email string"""
    if value is None:
        value = None
    elif isinstance(value, basestring):
        value = unicode(value)
    elif isinstance(value, (list, tuple)):
        value = u''.join(value)

    # strip empty spaces and lower address
    if isinstance(value, basestring):
        value = value.strip()
        value = value.lower()
    if isValidMailAddress(value):
        return value


# int
def intConverter(value):
    """Convert anything to an integer"""
    if not value:
        value = None
    elif isinstance(value, basestring):
        value = value.strip()
        value = int(value)
    return value


# list
def listConverter(value):
    """Convert anything to a list"""
    if not value:
        value = []
    elif isinstance(value, basestring):
        value = value.strip()
        value = [unicode(value)]
    elif isinstance(value, (list, tuple)):
        value = [unicode(v.strip()) for v in value if v]
    return value


# text
def textConverter(value):
    """Convert anything to text"""
    if value is None:
        value = None
    elif isinstance(value, basestring):
        value = unicode(value)
    elif isinstance(value, (list, tuple)):
        value = u' '.join(value)
    # strip empty spaces
    if isinstance(value, basestring):
        value = value.strip()
    return value


# textline
def textLineConverter(value):
    """Convert anything to textline"""
    if value is None:
        value = None
    elif isinstance(value, basestring):
        value = unicode(value)
    elif isinstance(value, (list, tuple)):
        value = u' '.join(value)
    
    # remove line breaks and strip empty spaces
    if isinstance(value, basestring):
        value = value.strip()
        value = value.replace('\n\r', ' ')
        value = value.replace('\n', ' ')
    return value


# uri (simple non ipv-6 uri yet)
_isuri = re.compile(
    # scheme
    r"[a-zA-z0-9+.-]+:"
    # non space (should be pickier)
    r"\S*$").match

def uriConverter(value):
    """Convert anything to an uri string"""
    if value is None:
        value = None
    elif isinstance(value, basestring):
        value = str(value)
    elif isinstance(value, (list, tuple)):
        value = u''.join(value)

    # strip empty spaces
    if isinstance(value, basestring):
        value = value.strip()
        value = value.replace(' ', '%20')
        if not _isuri(value):
            return None
    return value

def httpConverter(value):
    """Convert anything to a http or https uri string"""
    value = uriConverter(value)
    if value is not None and not (value.startswith('http://') or
                                  value.startswith('https://')):
        return None
    return value

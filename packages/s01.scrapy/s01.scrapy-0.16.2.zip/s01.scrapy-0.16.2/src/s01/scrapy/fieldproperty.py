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

import zope.schema

import scrapy.exceptions

_marker = object()


def listConverter(value):
    """Convert a list to a single item"""
    if isinstance(value, (list, tuple)):
        value = ' '.join(value)
    return value


class ScrapyFieldProperty(object):
    """Computed attributes based on zope.schema fields

    The field property provide default values, data validation and error
    messages based on data found in field meta-data.

    Note,
    The field property will gracefully hidde errors and use the default value
    on setting invalid values if required is not set to True. If required is
    set to True a scrapy.exceptions.DropItem exception is raised if the value
    is not valid.

    """

    def __init__(self, field, converter=None, serializer=None):
        self.__field = field
        self.__converter = converter
        self.__serializer = serializer
        self.__name = field.__name__
        self.__type = field._type
        self.__required = field.required
        if field.readonly:
            raise TypeError("Can't use readonly fields")

    def __get__(self, inst, klass):
        if inst is None:
            return self
        value = inst.__dict__.get(self.__name, _marker)
        if value is _marker:
            field = self.__field.bind(inst)
            value = getattr(field, 'default', None)
        # serialize value if a serializer is given
        if self.__serializer is not None:
            value = self.__serializer(value)
        return value

    def __set__(self, inst, value):
        # convert the value if a converter is given
        if self.__converter is not None:
            value = self.__converter(value)
        # validate the value
        field = self.__field.bind(inst)
        try:
            field.validate(value)
            inst.__dict__[self.__name] = value
        except zope.schema.ValidationError, e:
            if self.__required:
                # only raise error for required fields otherwise skip value
                raise scrapy.exceptions.DropItem(
                    "ValidationError(%s) for required field %s:%s" % (
                        e, self.__name,  value))

    def __getattr__(self, name):
        return getattr(self.__field, name)

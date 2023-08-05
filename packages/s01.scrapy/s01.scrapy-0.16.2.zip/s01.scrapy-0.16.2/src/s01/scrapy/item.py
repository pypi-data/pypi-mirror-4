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

import scrapy.item

_marker = object()


class ScrapyItemBase(scrapy.item.BaseItem):
    """Scrapy item based on zope.schema
    
    This scrapy item does NOT provide a dict API.
    
    The ScrapyItemBase class should use the ScrapyFieldProperty for define 
    the fields which offers validation and supports optional converter and
    serializer methods.

    Note: your custom scrapy item must implement an interface. This interface
    is used as the field schema and knows the field order if order matters
    in export (CSV).

    """

    def dump(self):
        """Dump the item field values based on the implemented interfaces to
        json data dict.
        """
        # Note, our data dict is not ordered. Take care if you use this data
        # if order matters, e.g. if you write to a CSV file. If you need to
        # order your export data use zope.schema.getFieldNamesInOrder(iface)
        # in your exporter for get the field ordered names. See zope.schema
        # for more info about field and schema
        data = {}
        for iface in zope.interface.providedBy(self):
            for name in zope.schema.getFieldNames(iface):
                data[name] = getattr(self, name, None)
        return data

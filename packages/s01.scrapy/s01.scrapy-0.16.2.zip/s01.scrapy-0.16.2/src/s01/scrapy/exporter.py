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

import csv
import os.path

import zope.interface
import zope.schema

import scrapy.exceptions
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

import s01.scrapy.util


class TestExporter(object):
    """Scrapy test data export pipeline"""

    def __init__(self, settings):
        self.settings = settings
        tmpDirPath = settings.get('S01_SCRAPY_TEST_EXPORT_DIR')
        if not tmpDirPath:
            raise scrapy.exceptions.NotConfigured
        fName = os.path.abspath(s01.scrapy.util.getNewFileName(tmpDirPath))
        self.file = open(fName, 'wb')
        self.writer = csv.writer(self.file)
        self.fieldNames = None
        dispatcher.connect(self.engine_stopped, signals.engine_stopped)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(crawler.settings)

    def _ensureHeaders(self, item):
        if self.fieldNames is None:
            self.fieldNames = []
            for iface in zope.interface.providedBy(item):
                for name in zope.schema.getFieldNamesInOrder(iface):
                    self.fieldNames.append(name)
            self.writer.writerow(self.fieldNames)

    def process_item(self, item, spider):
        """Get called for each item"""
        self._ensureHeaders(item)
        values = []
        append = values.append
        for name in self.fieldNames:
            value = getattr(item, name, None)
            if value is None:
                value = ''
            elif isinstance(value, unicode):
                value = value.encode('UTF-8')
            else:
                # convert anything else to a string, e.g. datetime
                value = str(value)
            append(value)
        self.writer.writerow(values)
        return item

    def engine_stopped(self):
        self.file.close()

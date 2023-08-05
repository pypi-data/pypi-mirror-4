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

import sys
import logging
import warnings

from twisted.python import log

import scrapy
import scrapy.log

# Logging levels
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
SILENT = CRITICAL + 1

level_names = {
    logging.DEBUG: "DEBUG",
    logging.INFO: "INFO",
    logging.WARNING: "WARNING",
    logging.ERROR: "ERROR",
    logging.CRITICAL: "CRITICAL",
    SILENT: "SILENT",
}


class Scrapy01FileLogObserver(log.FileLogObserver):
    """Scrapy file log observer with stderr error handling support"""

    def __init__(self, f, level=INFO, encoding='utf-8', crawler=None):
        self.level = level
        self.encoding = encoding
        self.crawler = crawler
        self.subprocessing = crawler.settings['LOG_FILE']
        log.FileLogObserver.__init__(self, f)

    def emit(self, eventDict):
        """Write log to sys.stderr which we can fetch in our parent process
        
        Also stop spider on error if STOP_CRAWLER_ON_ERROR is set
        """
        ev = scrapy.log._adapt_eventdict(eventDict, self.level, self.encoding)
        if ev is not None:
            log.FileLogObserver.emit(self, ev)
            if ev['logLevel'] >= ERROR:
                # stop crawling on errors
                if settings.getbool('STOP_CRAWLER_ON_ERROR'):
                    crawler.stop()
                msg = ev.get('message', 'ERROR')
                if msg:
                    msg = '%s\n' % ', '.join(msg)
                # we can't raise sys.exit(msg) because the twisted will catch
                # SystemError and log them, eeeek. But it should't matter
                # we still can get the error from stderr in our subprocess call
                sys.stderr.write(msg)
                sys.stdout.flush()


def start(logfile=None, loglevel='INFO', logstdout=None, logencoding='utf-8',
    crawler=None):
    settings = crawler.settings
    if not settings.getbool('LOG_ENABLED'):
        return

    if log.defaultObserver: # check twisted log not already started
        loglevel = scrapy.log._get_log_level(loglevel)
        logfile = logfile or settings['LOG_FILE']
        file = open(logfile, 'a') if logfile else sys.stderr
        if logstdout is None:
            logstdout = settings.getbool('LOG_STDOUT')
        sflo = Scrapy01FileLogObserver(file, loglevel, settings['LOG_ENCODING'],
            crawler)
        _oldshowwarning = warnings.showwarning
        log.startLoggingWithObserver(sflo.emit, setStdout=logstdout)
        # restore warnings, wrongly silenced by Twisted
        warnings.showwarning = _oldshowwarning
        scrapy.log.msg("Scrapy %s started (bot: %s)" % (scrapy.__version__, \
            settings['BOT_NAME']))

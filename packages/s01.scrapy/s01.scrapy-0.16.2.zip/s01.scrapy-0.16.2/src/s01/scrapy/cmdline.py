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
"""Scrapy command hookup using test settings
$Id:$
"""
__docformat__ = "reStructuredText"

import sys
import optparse
import os.path

import scrapy
import scrapy.cmdline
import scrapy.crawler

import s01.scrapy.util


# apply development settings
def execute(argv=None, settings=None):
    """Custom execute for buildout based spider packages"""
    if argv is None:
        argv = sys.argv
    else:
        # append additional args
        argv += sys.argv[1:]

    # override default settings with parts from test settings
    logFileName = None

    # override settings
    customLog = False
    if '--logfile' in argv:
        customLog = True

    # testing argument support
    testing = False
    if '--test' in argv:
        # first, remove unknown scrapy command
        argv.remove('--test')
        testing = True

    # additional testing marker support
    if settings['S01_SCRAPY_TESTING']:
        testing = True

    # if testing and no original logfile is used, set our log file
    # as default, check parts/log for output
    if testing and not customLog:
        # but not when --nolog get used
        logFileName = s01.scrapy.util.getLogFileName()
        logDir = os.path.dirname(logFileName)
        if not os.path.exists(logDir):
            print "Missing directory at %s" % logDir
            sys.exit(0)
        settings.overrides['LOG_ENABLED'] = True
        settings.overrides['LOG_FILE'] = logFileName

    if testing:
        # set our csv file exporter as default, check parts/tmp for output
        tmpDirPath = s01.scrapy.util.getTempDirPath()
        if not os.path.exists(tmpDirPath):
            print "Missing parts/tmp directory"
            sys.exit(0)
        settings.overrides['S01_SCRAPY_TEST_EXPORT_DIR'] = tmpDirPath
        settings.overrides['ITEM_PIPELINES'] = [
            's01.scrapy.exporter.TestExporter',
        ]

    # setup and install crawler
    crawler = scrapy.crawler.CrawlerProcess(settings)
    crawler.install()
    inproject = bool(settings.settings_module)
    cmds = scrapy.cmdline._get_commands_dict(settings, inproject)
    cmdname = scrapy.cmdline._pop_command_name(argv)
    parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(), \
        conflict_handler='resolve')
    if not cmdname:
        scrapy.cmdline._print_commands(settings, inproject)
        sys.exit(0)
    elif cmdname not in cmds:
        scrapy.cmdline._print_unknown_command(settings, cmdname, inproject)
        sys.exit(2)

    # execute command
    cmd = cmds[cmdname]
    parser.usage = "scrapy %s %s" % (cmdname, cmd.syntax())
    parser.description = cmd.long_desc()
    settings.defaults.update(cmd.default_settings)
    cmd.settings = settings
    cmd.add_options(parser)
    opts, args = parser.parse_args(args=argv[1:])
    scrapy.cmdline._run_print_help(parser, cmd.process_options, args, opts)
    cmd.set_crawler(crawler)
    # prevent log setup
    cmd.configured = True
    # now it's time to invoke our logger before the original logger get started,
    # this logger is responsible for print ERROR to stdout which is required
    # for check errors in subprocess calls
    import s01.scrapy.log
    s01.scrapy.log.start(logfile=logFileName, crawler=crawler)
    # setup crawler
    crawler.configure()

    scrapy.cmdline._run_print_help(parser, scrapy.cmdline._run_command, cmd, args, opts)

    sys.exit(cmd.exitcode)


if __name__ == '__main__':
    execute()

###############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Scrapy development tools

"""

import csv
import subprocess
import sys
import os
import optparse
from pprint import pprint

MARKER = object()

# execute command
def do(cmd, cwd=None):
    logger.debug('command: ' + cmd)
    stdout = stderr = subprocess.PIPE
    p = subprocess.Popen(
        cmd, stdout=stdout, stderr=stderr,
        shell=True, cwd=cwd)
    stdout, stderr = p.communicate()
    if stdout is None:
        stdout = "see output above"
    if stderr is None:
        stderr = "see output above"
    if p.returncode != 0:
        sys.exit(p.returncode)
    logger.debug('output: \n%s' % stdout)
    return stdout


# log analayzer
def readDataFile(fName):
    pass


class OperatorBase(object):
    """Supports several commands and knows the package structure"""

    path = None
    content = None
    lines = []
    data = []

    def __init__(self, cwdDir):
        self.logDir = os.path.normpath(os.path.join(cwdDir, 'parts', 'log'))
        self.tmpDir = os.path.normpath(os.path.join(cwdDir, 'parts', 'tmp'))


class LoggerOperator(OperatorBase):
    """Supports log file management"""

    def __init__(self, cwdDir, fileName):
        super(LoggerOperator, self).__init__(cwdDir)
        self.fileName = fileName
        self.path = os.path.join(self.logDir, self.fileName)
        if os.path.exists(self.path):
            f = open(self.path, 'rb')
            content = f.read()
            f.close()
            self.content = content.replace('\r', '')
            self.lines = self.content.split('\n')

    def dump(self, start=0, end=0):
        """Dumps the number of log file entries"""
        if end == 0:
            end = start + 1
        for line in self.lines[start:end]:
            print line

    def remove(self):
        """Remove the log file"""
        if self.path is not None and os.path.exists(self.path):
            os.remove(self.path)


class DataOperator(OperatorBase):
    """Supports tmp data file management"""

    def __init__(self, cwdDir, fileName):
        super(DataOperator, self).__init__(cwdDir)
        self.fileName = fileName
        if self.fileName == MARKER:
            names = os.listdir(self.tmpDir)
            if names:
                names.sort()
                names.reverse()
                self.fileName = names.pop(0)
                
        if self.fileName != MARKER:
            self.path = os.path.join(self.tmpDir, self.fileName)
            if os.path.exists(self.path):
                f = open(self.path, 'rb')
                content = f.read()
                f.close()
                self.content = content.replace('\r', '')
                self.lines = self.content.split('\n')
        
                # prepare json data
                header = None
                self.data = []
                for row in csv.reader(file(self.path)):
                    if header is None:
                        header = row
                    else:
                        d = {}
                        for i, label in enumerate(header):
                            d[label] = row[i]
                        self.data.append(d)

    def dump(self, start=0, end=0):
        """Dumps the number of log file entries"""
        if end == 0:
            end = start + 1
        for data in self.data[start:end]:
            pprint(data)

    def remove(self):
        """Remove the log file"""
        if self.path is not None and os.path.exists(self.path):
            os.remove(self.path)


# options
usage = """usage: script-name <command> [options]
usage: logger [dump|remove] [options]
usage: data [dump|remove] [options]

"""
# logger options
loggerOptions = optparse.OptionParser(usage)

loggerOptions.add_option(
    "-f", "--filename", dest="filename", default="testing.log",
    help="[dump|remove] The log file name located in parts/log without folder path")

loggerOptions.add_option(
    "-s", "--start", dest="start", default=0, type='int',
    help="[dump] Start number for log entry to dump")

loggerOptions.add_option(
    "-e", "--end", dest="end", default=0, type='int',
    help="[dump] End number for entry to dump")

# data options
dataOptions = optparse.OptionParser(usage)

dataOptions.add_option(
    "-f", "--filename", dest="filename", default=MARKER,
    help="[dump|remove] The data file name located in parts/tmp without folder path")

dataOptions.add_option(
    "-s", "--start", dest="start", default=0, type='int',
    help="[dump] Start number for log entry to dump")

dataOptions.add_option(
    "-e", "--end", dest="end", default=0, type='int',
    help="[dump] End number for entry to dump")


def logger(args=None):
    if args is None:
        args = sys.argv[1:]
    if not args:
        args = ['-h']

    # pop additional args with option parser
    options, args = loggerOptions.parse_args(args)

    cmd = None
    if len(args) == 0:
        print "script-name and method name are missing"
    elif len(args) == 1:
        cmd = args[0]
    elif len(args) > 1:
        print "too much arguments given"

    cwdDir = os.getcwd()
    try:
        # parse arguments
        operator = LoggerOperator(cwdDir, options.filename)
        if cmd == 'dump':
            operator.dump(options.start, options.end)
        if cmd == 'remove':
            operator.remove()
    except KeyboardInterrupt:
        sys.exit(0)

    sys.exit(0)


def data(args=None):
    if args is None:
        args = sys.argv[1:]
    if not args:
        args = ['-h']

    # pop additional args with option parser
    options, args = dataOptions.parse_args(args)

    cmd = None
    if len(args) == 0:
        print "script-name and method name are missing"
    elif len(args) == 1:
        cmd = args[0]
    elif len(args) > 1:
        print "too much arguments given"

    cwdDir = os.getcwd()
    try:
        # parse arguments
        operator = DataOperator(cwdDir, options.filename)
        if cmd == 'dump':
            operator.dump(options.start, options.end)
        if cmd == 'remove':
            operator.remove()
    except KeyboardInterrupt:
        sys.exit(0)

    sys.exit(0)

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
"""Scrapy buildout based spider development and deployment recipes

"""

import logging
import os
import os.path
import sys
import pkg_resources
import zc.buildout
import zc.recipe.egg

isWin32 = sys.platform == 'win32'


def asBool(obj):
    if isinstance(obj, basestring):
        obj = obj.lower()
        if obj in ('1', 'true', 'yes', 't', 'y'):
            return True
        if obj in ('0', 'false', 'no', 'f', 'n'):
            return False
    return bool(obj)


def fixEscape(value):
    """Recursive fix escape in value"""
    if isinstance(value, basestring) and (
        '\t' in value or '\n' in value or r'\x' in value):
        # fix bad string escape
        value = value.replace('\t', '\\t')
        value = value.replace('\n', '\\n')
        value = value.replace(r'\x', r'\\x')
        value = value.replace('\\\r', '\\r')
        value = value.replace('\\\n', '\\n')
        value = value.replace(r'\\\x', r'\\x')
    elif isinstance(value, list):
        value = [fixEscape(v) for v in value]
    elif isinstance(value, dict):
        for k, v in value.items():
            value[fixEscape(k)] = fixEscape(v)
    return value


def fixPath(value):
    """Windows path cleanup hack, hope this will not messup with some values"""
    if isWin32:
        if isinstance(value, basestring) and ('\t' in value or '\n' in value):
            # fix some escape char first
            value = value.replace('\t', '\\t')
            value = value.replace('\n', '\\n')
            value = value.replace('\\\r', '\\r')
            value = value.replace('\\\n', '\\n')
            # fix path separator
            value = value.replace('\\', '/')
        elif isinstance(value, list):
            value = [fixPath(v) for v in value]
        elif isinstance(value, dict):
            for k, v in value.items():
                value[k] = fixPath(v)
    return value


def _relativize(base, path):
    base += os.path.sep
    if isWin32:
        # windoze paths are case insensitive, but startswith is not
        base = base.lower()
        path = path.lower()

    if path.startswith(base):
        path = 'join(base, %r)' % path[len(base):]
    else:
        path = repr(path)
    return path


class LoggerMixin(object):
    """Logging support."""

    _loggerName = None
    _logger = None

    @apply
    def loggerName():
        def fget(self):
            return self._loggerName
        def fset(self, loggerName):
            self._loggerName = loggerName
            self._logger = logging.getLogger(self._loggerName)
        return property(fget, fset)

    @property
    def logger(self):
        if self._logger is None:
            self._logger = logging.getLogger(self.loggerName)
        return self._logger


class CHMODMixin(LoggerMixin):
    """chmode support."""

    def doChmod(self, filename, mode):
        if not filename or not mode:
            return
        os.chmod(filename, self.mode)
        msg = "Change mode %s for %s" % (mode, filename)
        self.logger.info(msg)


environment_template = """# environment
import os
sys.argv[0] = os.path.abspath(sys.argv[0])

# get settings
import scrapy.utils.project
settings = scrapy.utils.project.get_project_settings()
# fake inproject marker, see cmdline for more info
settings.settings_module = True
# settings overrides
"""

test_environment_template = """# test environment
import os
sys.argv[0] = os.path.abspath(sys.argv[0])
os.chdir(%s)

# get settings
import scrapy.utils.project
settings = scrapy.utils.project.get_project_settings()
# fake inproject marker, see cmdline for more info
settings.settings_module = True
# settings overrides
"""

env_template = """os.environ['%s'] = %r
"""

settings_overrides_template = """settings.overrides['%s'] = %r
"""

initialization_template = """
# initialization
%s

"""

export_settings = """
# export settings to s01.scrapy.util
import s01.scrapy.util
s01.scrapy.util.settings = settings
"""

bootstrap_template = """
# bootstrap
%s
"""


# TODO: check zc.testrunner which uses a parts/*/site-packages setup
#       probably we should also use such a setup and allow better separate
#       form the system ypthon
class ScrapyRecipeBase(LoggerMixin):
    """Base class for scrapy script recipes"""

    def __init__(self, buildout, name, options):
        self.egg = None
        self._wd = None
        self.buildout = buildout
        self.name = name
        self.options = options
        options['script'] = os.path.join(buildout['buildout']['bin-directory'],
                                         options.get('script', self.name),
                                         )
        if not options.get('working-directory', ''):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'], name)

        if options.get('eggs'):
            self.egg = zc.recipe.egg.Egg(buildout, name, options)

        # by default log to the s01.worker logger
        self.loggerName = options.get('logger', 's01.worker')

    @property
    def wd(self):
        if self._wd is None:
            wd = self.options.get('working-directory', '')
            if not wd:
                wd = self.options['location']
                if os.path.exists(wd):
                    assert os.path.isdir(wd)
                else:
                    os.mkdir(wd) # makedirs
                    self.generated.append(wd)
            wd = os.path.abspath(wd)
            if self.egg._relative_paths:
                self._wd = _relativize(self.egg._relative_paths, wd)
            else:
                self._wd = repr(wd)
        return self._wd

    @property
    def arguments(self):
        # raise error if used and not set in recipe
        return self.options['arguments']

    @property
    def module(self):
        return self.options.get('module', 's01.scrapy.cmdline')

    @property
    def method(self):
        return self.options.get('method', 'execute')

    @property
    def testing(self):
        return asBool(self.options.get('testing', False))

    @property
    def environment_template(self):
        return environment_template

    def validate(self):
        # by default it's allowed to use without settings
        pass

    def install(self):
        self.generated = []
        options = self.options
        executable = self.buildout['buildout']['executable']
        self.settings = options.get('settings', None)
        self.overrides = options.get('overrides', '')

        # setup additional egg path
        if self.egg:
            extra_paths = self.egg.extra_paths
            eggs, ws = self.egg.working_set()
        else:
            extra_paths = ()
            ws = []

        # collect settings, settings could be a section with a target or
        # a file path. You can use the p01.scrapy:settings recipe for create
        # a file with such a section target or just point to an existing file
        # path
        data = {}
        if self.settings:
            section = self.buildout.get(self.settings)
            if section:
                # it's a section and not a file, load it from target
                sPath = section['target']
                self.logger.info('Load settings given from section target %s'  %
                    sPath)
            else:
                sPath = os.path.abspath(self.settings)
                self.logger.info('Load settings from path %s' % sPath)
            if not os.path.exists(sPath):
                msg = 'Missing settings path %s' % sPath
                self.logger.info(msg)
                raise zc.buildout.UserError(msg)
            # load given settings file into dict
            source = open(sPath, 'rb')
            # no fix escape required because we already converted path like
            # \x to /x in settings file generation
            exec source in data
            # remove __builtins__
            del data['__builtins__']

        # merge additional settings given as overrides key/values into data
        if self.overrides:
            self.logger.info('Load overrides')
            oData = {}
            overrides = self.overrides
            # fix bad escape if a path contains `\x`
            overrides = overrides.replace(r'\x', r'\\x')
            overrides = overrides.replace(r'\\\x', r'\\x')
            exec overrides in oData
            # remove __builtins__
            del oData['__builtins__']
            for k, v in oData.items():
                # fix path
                oData[k] = fixPath(v)
            # update data with overrides key, values
            data.update(oData)

        # initialize settings data
        initialization = self.environment_template
        env_section = self.options.get('environment', '').strip()
        if env_section:
            env = self.buildout[env_section]
            for key, value in env.items():
                initialization += env_template % (key, value)

        initialization_section = options.get('initialization', '').strip()
        if initialization_section:
            initialization += initialization_template % initialization_section

        for key, value in data.items():
            value = fixEscape(value)
            initialization += settings_overrides_template % (key, value)

        # setup testing marker
        if self.testing:
            self.logger.info('Enable testing option')
            initialization += settings_overrides_template % (
                'S01_SCRAPY_TESTING', True)

        # export settings
        initialization += export_settings

        bootstrap = options.get('bootstrap', '').strip()
        if bootstrap:
            initialization += bootstrap_template % bootstrap

        # validate
        self.validate()

        # setup script
        self.generated.extend(zc.buildout.easy_install.scripts(
            [(options['script'], self.module, self.method)],
            ws, executable, self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = self.arguments,
            initialization = initialization,
            ))
        return self.generated

    update = install


# scripts without settings
class ScrapyRecipe(ScrapyRecipeBase):
    """Scrapy script recipe"""

    @property
    def arguments(self):
        return self.options.get('arguments', "['scrapy'], settings")


class TestRecipe(ScrapyRecipeBase):
    """Scrapy test recipe"""

    @property
    def module(self):
        return self.options.get('module', 'zope.testrunner')

    @property
    def method(self):
        return self.options.get('method', 'run')

    @property
    def environment_template(self):
        return test_environment_template % self.wd

    @property
    def arguments(self):
        eggs, ws = self.egg.working_set(('zope.testrunner', ))
        test_paths = [ws.find(pkg_resources.Requirement.parse(spec)).location
                      for spec in eggs]
        if self.egg._relative_paths:
            test_paths = [_relativize(self.egg._relative_paths, p)
                          for p in test_paths]
        else:
            test_paths = map(repr, test_paths)
        paths = ''.join(("        '--test-path', %s,\n" % p) for p in test_paths)
        return ('[\n'+ paths +'        ]')


# scripts with required overrides or settings
class SettingsRequiredMixin(object):
    """Check missing settings"""

    def validate(self):
        # check if we have settings
        if not (self.settings or self.overrides):
            raise zc.buildout.UserError("At least one of settings file or " \
                                        "overrides key/values is required")


class CrawlRecipe(SettingsRequiredMixin, ScrapyRecipeBase):
    """Scrapy crawl script recipe"""

    @property
    def arguments(self):
        return "['scrapy', 'crawl'], settings"


class ListRecipe(SettingsRequiredMixin, ScrapyRecipeBase):
    """Scrapy list script recipe"""

    @property
    def arguments(self):
        return "['scrapy', 'list'], settings"


class SettingsRecipe(CHMODMixin):
    """Create settings file based on file path using file(path, 'w')
    because of path convertion.
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.options = options
        self.name = name
        self.mode = int(options.get('mode', '0644'), 8)
        # touch content, raises error if missing
        options['content']
        self.originalPath = options['target']
        options['target'] = os.path.join(buildout['buildout']['directory'],
            self.originalPath)
        self.createPath = options.get('createpath', 'False').lower() in [
            'true', 'on', '1']

        # by default log to the s01.worker logger
        self.loggerName = options.get('logger', 's01.worker')

    def install(self):
        target = self.options['target']
        dirname = os.path.dirname(target)
        if not os.path.isdir(dirname):
            self.logger.info('Creating directory %s', dirname)
            os.makedirs(dirname)
        f = file(target, 'w')
        self.logger.info('Writing file %s', target)
        content = self.options['content']
        # Windows path cleanup hack, hope this will not messup
        content = content.replace('\\', '/')
        f.write(content)
        f.close()
        self.doChmod(target, self.mode)
        return target

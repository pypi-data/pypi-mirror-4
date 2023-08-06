# Copyright (c) 2003-2010 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
"""APyCoT, A Pythonic Code Tester

this is the bot part of the code tester, responsible to execute checks
"""
__docformat__ = "restructuredtext en"

import os
import sys
import stat
from os.path import exists, join, dirname
from subprocess import STDOUT, Popen
from tempfile import TemporaryFile

from logilab.common.textutils import splitstrip

from cubes import narval # ensure narvalbot is importable

from narvalbot.prototype import action, input

# regitry of available repositories, preprocessors and checkers

REGISTRY = {'repository': {},
            'preprocessor': {},
            'checker': {}}

def register(category, klass):
    """register a class"""
    REGISTRY[category][klass.id] = klass

def get_registered(category, name):
    """get a object by name"""
    try:
        return REGISTRY[category][name]
    except KeyError:
        raise ConfigError('No object %r in category %r' % (name, category))

# apycot standard exception ####################################################

class ConfigError(Exception):
    """exception due to a wrong user configuration"""

class SetupException(Exception):
    """raised in the setup step"""


def not_executed_checker(id):
    """useful helper decorator to force execution to report further action
    failures into apycot report
    """
    def function(step, id=id):
        plan = step.plan
        if hasattr(plan, 'apycot'):
            test = plan.apycot
            test.run_checker(id, nonexecuted=True)
    return function

def apycotaction(id, *conditions):
    """apycotaction : narval action + 'apycot' input being the :class:`Test`
    instance and 'options' optional input containing configuration options
    (:class:`narvalbot.elements.Options`)
    """
    def decorator(func, id=id):
        return input('apycot', 'isinstance(elmt, Test)', *conditions)(
            input('options', 'isinstance(elmt, Options)', optional=True)(
                action('apycot.%s' % id, nonexecuted=not_executed_checker(id))(func)
                )
            )
    return decorator


# check statuses ###############################################################

class TestStatus(object):
    __all = {}

    def __init__(self, name, order, nonzero):
        self.name = name
        self.order = order
        self.nonzero = nonzero
        self.__all[name] = self

    def __int__(self):
        return self.order

    def __nonzero__(self):
        return self.nonzero

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<TestStatus %s>" % self.name

    def __cmp__(self, other):
        return cmp(int(self), int(other))

    @classmethod
    def get(cls, name):
        return cls.__all.get(name)

# keep order for bw compat
SKIPPED = TestStatus('skipped',  -5, False) # Checker not even launched
KILLED  = TestStatus('killed',   -3, False) # Checker killed (for limit reason)
ERROR   = TestStatus('error',    -1, False) # Unexpected error during chks exec
FAILURE = TestStatus("failure",   0, False) # Project failed the check
NODATA  = TestStatus('nodata',    2, False) # No data found in the project
PARTIAL = TestStatus('partial',   5, True)  # Project partially pass th check
SUCCESS = TestStatus('success',  10, True)  # Project succeed the check


# base class for all apycot objects ############################################

_MARKER = ()

class ApycotObject(object):
    """base class for apycot checkers / preprocessors"""
    options_def = {}
    status = None

    def __init__(self, writer, options=None):
        self.writer = writer
        if options is None:
            options = {}
        self.options = options

    @staticmethod
    def merge_status(global_status, status):
        if global_status is None:
            return status
        elif status is None:
            return global_status
        else:
            return min(global_status, status)

    def set_status(self, status):
        self.status = self.merge_status(self.status, status)

    def record_version_info(self, versionof, version):
        self.writer.info(version, path=versionof)

    def check_options(self):
        """check mandatory options have a value (I know I know...) and set
        defaults
        """
        for optname, optdict in self.options_def.iteritems():
            assert hasattr(optdict, 'get'), "optdict : %s ; self.options : %s" % (optdict, self.options)
            if optdict.get('required') and not self.options.get(optname):
                raise ConfigError('missing/empty value for option %r' % optname)
            if not optname in self.options:
                self.options[optname] = optdict.get('default')
            opttype = optdict.get('type')
            if opttype is None:
                continue
            if opttype == 'int':
                self.options[optname] = int(self.options[optname])
            elif opttype == 'csv':
                if self.options[optname]:
                    if isinstance(self.options[optname], basestring):
                        self.options[optname] = splitstrip(self.options[optname])
                else:
                    self.options[optname] = []
            else:
                raise Exception('Unknow option type %s for %s' % (opttype, optname))


# base class for external commands handling ####################################

class OutputParser(ApycotObject):
    non_zero_status_code = ERROR
    status = SUCCESS

    def __init__(self, writer, options=None, path=None):
        super(OutputParser, self).__init__(writer, options)
        self.unparsed = None
        self.path = path

    def parse_line(self, line):
        self.unparsed.append(line.strip())

    def parse(self, stream):
        self.unparsed = []
        self._parse(stream)
        return self.status

    def _parse(self, stream):
        for line in stream:
            line = line.strip()
            if line:
                self.parse_line(unicode(line, 'utf8', 'replace'))

class SimpleOutputParser(OutputParser):

    PREFIX_INFO = ('I',)
    PREFIX_WARNING = ('W',)
    PREFIX_FAILURE = ('E',)
    PREFIX_FATAL = ('F', 'C')

    def map_message(self, mtype, msg):
        if mtype in self.PREFIX_INFO:
            self.writer.info(msg, path=self.path)
        elif mtype in self.PREFIX_WARNING:
            self.writer.warning(msg, path=self.path)
        elif mtype in self.PREFIX_FAILURE:
            self.writer.error(msg, path=self.path)
            self.set_status(FAILURE)
        elif mtype in self.PREFIX_FATAL:
            self.writer.fatal(msg, path=self.path)
            self.set_status(FAILURE)
        elif msg:
            self.unparsed.append(msg)

    def parse_line(self, line):
        line_parts = line.split(':', 1)
        if len(line_parts) > 1:
            mtype, msg = line_parts
            self.map_message(mtype.strip(), msg.strip())
        else:
            self.unparsed.append(line.strip())


class Command(ApycotObject):
    non_zero_status_code = ERROR
    status = SUCCESS

    def __init__(self, writer, command, parsed_content='merged',
                 raises=False, shell=False, path=None, cwd=None):
        super(Command, self).__init__(writer)
        assert command, command
        self.command = command
        self.parsed_content = parsed_content
        self.raises = raises
        self.shell = shell
        self.path = path
        self.cwd = cwd
        self._cmd_printed = False

    @property
    def commandstr(self):
        if not isinstance(self.command, basestring):
            return ' '.join(self.command)
        return self.command

    def run(self):
        """actually run the task by spawning a subprocess"""
        outfile = TemporaryFile(mode='w+', bufsize=0)
        if self.parsed_content == 'merged':
            errfile = STDOUT
        else:
            errfile = TemporaryFile(mode='w+', bufsize=0)
        try:
            cmd = Popen(self.command, bufsize=0,
                        stdout=outfile, stderr=errfile, stdin=open('/dev/null', 'a'),
                        shell=self.shell, cwd=self.cwd)
        except OSError, err:
            raise ConfigError(err)
        cmd.communicate()
        if self.parsed_content == 'merged':
            outfile.seek(0)
            self.handle_output(cmd.returncode, outfile, None)
        else:
            for stream in (outfile, errfile):
                stream.seek(0)
            if not os.fstat(errfile.fileno())[stat.ST_SIZE]:
                errfile = None
            if not os.fstat(outfile.fileno())[stat.ST_SIZE]:
                outfile = None
            self.handle_output(cmd.returncode, outfile, errfile)
        return self.status

    def handle_output(self, status, stdout, stderr):
        stdout, stderr, unparsed = self.process_output(stdout, stderr)
        cmd = self.commandstr
        path = self.path or cmd
        if status:
            if status > 0:
                short_msg = u'`%s` returned with status : %s' % (cmd, status)
                cmd_status = self.non_zero_status_code
            else:
                # negative status mean the process have been killed by a signal
                short_msg = u'`%s` killed by signal %s' % (cmd, status)
                # Get the signal number
                status *= -1
                cmd_status = KILLED
                # XXX we need detection of common limit here
            msg = self.append_output_messages(short_msg, stdout, stderr, unparsed)
            self.writer.error(msg, path=path)
            self.set_status(cmd_status)
            if self.raises:
                raise SetupException(short_msg)
        else:
            msg = self.append_output_messages(u'`%s` executed successfuly' % cmd,
                                              stdout, stderr, unparsed)
            self.writer.debug(msg, path=path)

    def append_output_messages(self, msg, stdout, stderr, unparsed):
        if stdout is not None:
            stdout = unicode(stdout.read(), 'utf8', 'replace')
            if stdout:
                if self.parsed_content == 'merged':
                    msg += u'\noutput:\n%s' % stdout
                else:
                    msg += u'\nstandard output:\n%s' % stdout
        if stderr is not None:
            stderr = unicode(stderr.read(), 'utf8', 'replace')
            if stderr:
                msg += u'\nerror output:\n%s' % stderr
        if unparsed:
            msg += u'\nunparsed output:\n%s' % unparsed
        return msg

    def process_output(self, stdout, stderr):
        return stdout, stderr, None


class ParsedCommand(Command):
    def __init__(self, writer, command, parsercls=SimpleOutputParser, **kwargs):
        Command.__init__(self,  writer, command, **kwargs)
        self.parser = parsercls(writer)
        self.parser.path = self.path
        self.non_zero_status_code = self.parser.non_zero_status_code

    def process_output(self, stdout, stderr):
        if stdout is not None and self.parsed_content in ('stdout', 'merged'):
            self.status = self.parser.parse(stdout)
            return None, stderr, u'\n'.join(self.parser.unparsed)
        if stderr is not None and self.parsed_content == 'stderr':
            self.status = self.parser.parse(stderr)
            return stdout, None, u'\n'.join(self.parser.unparsed)
        return stdout, stderr, None


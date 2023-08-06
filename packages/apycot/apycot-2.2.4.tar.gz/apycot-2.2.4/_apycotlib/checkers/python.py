"""checkers for python source files

:organization: Logilab
:copyright: 2003-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
from __future__ import with_statement

__docformat__ = "restructuredtext en"

import os
import sys
import re
from commands import getoutput
from os.path import join, exists
from test import test_support
from warnings import warn
from lxml import etree


from logilab.common.testlib import find_tests
from logilab.common.modutils import get_module_files
from logilab.common.decorators import cached
from logilab.common.compat import any
from logilab.common.proc import RESOURCE_LIMIT_EXCEPTION

try:
    import coverage
    if coverage.__version__ < "3":
        raise ImportError
    COVERAGE_CMD = "/usr/bin/python-coverage" # XXX
except ImportError:
    coverage = None

from apycotlib import register
from apycotlib import SUCCESS, FAILURE, PARTIAL, NODATA, ERROR
from apycotlib import SimpleOutputParser, ParsedCommand
from apycotlib.checkers import BaseChecker, AbstractFilteredFileChecker
from apycotlib.preprocessors.distutils import INSTALL_PREFIX, pyversions

def pyinstall_path(test):
    path = _pyinstall_path(test)
    if not exists(path):
        raise Exception('path %s doesn\'t exist' %  path)
    return path

@cached
def _pyinstall_path(test):
    """return the project's installation path"""
    config = test.apycot_config()
    if 'install_path' in config:
        return config['install_path']
    modname = config.get('python_modname')
    if not modname and exists(join(test.tmpdir, test.project_path(), '__pkginfo__.py')):
        from logilab.devtools.lib.pkginfo import PackageInfo
        pkginfo = PackageInfo(directory=test.project_path())
        modname = pkginfo.modname
        distname = pkginfo.distname or modname
        package = pkginfo.subpackage_of
        if modname and package:
            modname = '%s.%s' % (package, modname)
        elif distname.startswith('cubicweb-'):
            cubespdir = join(os.environ['APYCOT_ROOT'], 'local', 'share', 'cubicweb')
            pypath = cubespdir + os.pathsep + os.environ.get('PYTHONPATH', '')
            test.update_env(test.tconfig.name, 'PYTHONPATH', pypath, os.pathsep)
            return join(cubespdir, 'cubes', modname)
    if modname:
        try:
            path = join(INSTALL_PREFIX[test.project_path()], *modname.split('.'))
        except KeyError:
            pass
        else:
            cfg = test.apycot_config()
            if cfg.get('subpath'):
                path = join(path, cfg['subpath'])
            return path
    return test.project_path(subpath=True)


class PythonSyntaxChecker(AbstractFilteredFileChecker):
    """check syntax of python file

       Use Pylint to check a score for python package. The check fails if the score is
       inferior to a given threshold.
    """
    id = 'python_syntax'
    checked_extensions = ('.py', )

    def check_file(self, filepath):
        """try to compile the given file to see if it's syntaxicaly correct"""
        # Try to compile it. If compilation fails, then there's a
        # SyntaxError
        try:
            compile(open(filepath, 'U').read() + '\n', filepath, "exec")
            return SUCCESS
        except SyntaxError, error:
            self.writer.error(error.msg, path=filepath, line=error.lineno)
            return FAILURE

    def version_info(self):
        self.record_version_info('python', sys.version)

register('checker', PythonSyntaxChecker)


class PyTestParser(SimpleOutputParser):
    status = NODATA
    non_zero_status_code = FAILURE
    # search for following output:
    #
    # 'Ran 42 test cases in 0.07s (0.07s CPU), 3 errors, 31 failures, 3 skipped'
    regex = re.compile(
        r'Ran (?P<total>[0-9]+) test cases '
        'in (?P<time>[0-9]+(.[0-9]+)?)s \((?P<cputime>[0-9]+(.[0-9]+)?)s CPU\)'
        '(, )?'
        '((?P<errors>[0-9]+) errors)?'
        '(, )?'
        '((?P<failures>[0-9]+) failures)?'
        '(, )?'
        '((?P<skipped>[0-9]+) skipped)?'
        )

    total, failures, errors, skipped = 0, 0, 0, 0

    def __init__(self, writer, options=None):
        super(PyTestParser, self).__init__(writer, options)
        self.total    = 0
        self.failures = 0
        self.skipped  = 0
        self.errors   = 0

    def _parse(self, stream):
        self.status = None
        super(PyTestParser, self)._parse(stream)
        if self.errors or self.failures:
            self.set_status(FAILURE)
        elif self.skipped:
            self.set_status(PARTIAL)
        elif not self.total:
            self.set_status(NODATA)
        elif self.total >= 0:
            self.set_status(SUCCESS)

    @property
    def success(self):
        return max(0, self.total - sum(( self.failures, self.errors,
                                         self.skipped,)))
    def add_junk(self, line):
        if any(c for c in line if c not in 'EFS. \n\t\r-*'):
            self.unparsed.append(line)

    def extract_tests_status(self, values):
        for status in ('failures', 'errors', 'skipped'):
            try:
                setattr(self, status,
                        max(getattr(self, status), int(values[status])))
            except TypeError:
                pass

    def parse_line(self, line):
        match = self.regex.match(line)
        if match is not None:
            values = match.groupdict()
            total = int(values['total'])
            self.total += total
            self.extract_tests_status(values)
        else:
            self.add_junk(line)

PYVERSIONS_OPTIONS = {
    'tested_python_versions': {
        'type': 'csv',
        'help': ('comma separated list of python version (such as 2.5) that '
                 'should be considered for testing.'),
        },
    'ignored_python_versions': {
        'type': 'csv',
        'help': ('comma separated list of python version (such as 2.5) that '
                 'should be ignored for testing when '
                 'use_pkginfo_python_versions is set to 1.'),
        },
    'use_pkginfo_python_versions': {
        'type': 'int', 'default': True,
        'help': ('0/1 flag telling if tested python version should be '
                 'determinated according to __pkginfo__.pyversion of the '
                 'tested project. This option is ignored if tested_python_versions '
                 'is set.'),
        },
    'pycoverage': {
        'type': 'int', 'default': False,
        'help': ('Tell if test should be run with pycoverage to gather '
                 'coverage data.'),
        },
    }

class PyTestChecker(BaseChecker):
    """check that unit tests of a python package succeed using the pytest command
    (from logilab.common)
    """
    id = 'pytest'
    need_preprocessor = 'install'
    parsercls = PyTestParser
    parsed_content = 'stdout'
    options_def = PYVERSIONS_OPTIONS.copy()
    options_def.update({
        'pytest.extra_argument': {
            'type': 'string',
            'help': ('extra argument to give to pytest. Add this option multiple '
                     'times in the correct order to give several arguments.'),
            },
        })

    def __init__(self, writer, options=None):
        BaseChecker.__init__(self, writer, options)
        self._path = None
        self.test = None

    def version_info(self):
        if pyversions(self.test):
            self.record_version_info('python', ', '.join(pyversions(self.test)))

    def enable_coverage(self):
        if self.options.get('pycoverage') and coverage:
            self.coverage_data = join(self.cwd, '.coverage')
            # XXX we need the environment variable to be considered by
            # "python-coverage run"
            os.environ['COVERAGE_FILE'] = self.coverage_data
            return True
        return False

    def setup_check(self, test):
        """run the checker against <path> (usually a directory)"""
        test_support.verbose = 0
        self.test = test
        self.cwd = test.project_path(subpath=True)
        if not pyversions(self.test):
            self.writer.error('no required python version available')
            return ERROR
        return SUCCESS

    def do_check(self, test):
        if self.enable_coverage():
            command = ['-c', 'from logilab.common.pytest import run; import sys; sys.argv=["pytest", "--coverage"]; run()']
        else:
            command = ['-c', 'from logilab.common.pytest import run; run()']
        extraargs = self.options.get("pytest.extra_argument", [])
        if not isinstance(extraargs, list):
            command.append(extraargs)
        else:
            command += extraargs
        status = SUCCESS
        testresults = {'success': 0, 'failures': 0,
                       'errors': 0, 'skipped': 0}
        total = 0
        for python in pyversions(self.test):
            cmd = self.run_test(command, python)
            for rtype in testresults:
                total += getattr(cmd.parser, rtype)
                testresults[rtype] += getattr(cmd.parser, rtype)
            status = self.merge_status(status, cmd.status)
        self.execution_info(total, testresults)
        return status

    def execution_info(self, total, testresults):
        self.writer.raw('total_test_cases', total, 'result')
        self.writer.raw('succeeded_test_cases', testresults['success'], 'result')
        self.writer.raw('failed_test_cases', testresults['failures'], 'result')
        self.writer.raw('error_test_cases', testresults['errors'], 'result')
        self.writer.raw('skipped_test_cases', testresults['skipped'], 'result')

    def get_command(self, command, python):
        return [python, '-W', 'ignore'] + command

    def run_test(self, command, python='python'):
        """execute the given test file and parse output to detect failed /
        succeed test cases
        """
        if isinstance(command, basestring):
            command = [command]
        command = self.get_command(command, python)
        cmd = ParsedCommand(self.writer, command,
                            parsercls=self.parsercls,
                            parsed_content=self.parsed_content,
                            path=self._path, cwd=self.cwd)
        cmd.run()
        cmd.set_status(cmd.parser.status)
        return cmd

register('checker', PyTestChecker)


class PyUnitTestParser(PyTestParser):
    result_regex = re.compile(
        r'(OK|FAILED)'
        '('
        ' \('
        '(failures=(?P<failures>[0-9]+))?'
        '(, )?'
        '(errors=(?P<errors>[0-9]+))?'
        '(, )?'
        '(skipped=(?P<skipped>[0-9]+))?'
        '\)'
        ')?')

    total_regex = re.compile(
        'Ran (?P<total>[0-9]+) tests?'
        ' in (?P<time>[0-9]+(.[0-9]+)?s)')

    def parse_line(self, line):
        match = self.total_regex.match(line)
        if match is not None:
            self.total = int(match.groupdict()['total'])
            return
        match = self.result_regex.match(line)
        if match is not None:
            self.extract_tests_status(match.groupdict())
            return
        self.add_junk(line)


class PyUnitTestChecker(PyTestChecker):
    """check that unit tests of a python package succeed

    Execute tests found in the "test" or "tests" directory of the package. The
    check succeed if no test cases failed. Note each test module is executed by
    a spawed python interpreter and the output is parsed, so tests should use
    the default text output of the unittest framework, and avoid messages on
    stderr.

    spawn unittest and parse output (expect a standard TextTestRunner)
    """
    id = 'pyunit'
    parsed_content = 'stderr'
    parsercls = PyUnitTestParser
    options_def = PYVERSIONS_OPTIONS.copy()
    options_def.update({
        'test_dirs': {
            'type': 'csv', 'default': ('test', 'tests'),
            'help': ('comma separated list of directories where tests could be '
                     'find. Search in "test" and "tests by default.'),
            },
        })

    def do_check(self, test):
        status = SUCCESS
        testdirs = self.options.get("test_dirs")
        basepath = test.project_path(subpath=True)
        for testdir in testdirs:
            testdir = join(basepath, testdir)
            if exists(testdir):
                self._path = testdir
                _status = self.run_tests(testdir)
                status = self.merge_status(status, _status)
                break
        else:
            self.writer.error('no test directory', path=basepath)
            status = NODATA
        return status

    def run_tests(self, testdir):
        """run a package test suite
        expect to be in the test directory
        """
        tests = find_tests(testdir, remove_suffix=False)
        if not tests:
            self.writer.error('no test found', path=self._path)
            return NODATA
        status = SUCCESS
        testresults = {'success': 0, 'failures': 0,
                       'errors': 0, 'skipped': 0}
        total = 0
        for python in pyversions(self.test):
            for test_file in tests:
                cmd = self.run_test(join(testdir, test_file), python)
                total += cmd.parser.total
                for rtype in testresults:
                    testresults[rtype] += getattr(cmd.parser, rtype)
                if cmd.status == NODATA:
                    self.writer.error('no test found', path=test_file)
                status = self.merge_status(status, cmd.status)
        self.execution_info(total, testresults)
        return status

    def get_command(self, command, python):
        python = [python, '-W', 'ignore']
        if self.enable_coverage():
            python += [COVERAGE_CMD, 'run', '-a', '--branch',
                       '--source=%s' % pyinstall_path(self.test)]
        return python + command

register('checker', PyUnitTestChecker)


class PyDotTestParser(PyUnitTestParser):
    line_regex = re.compile(
            r'(?P<filename>\w+\.py)(\[(?P<ntests>\d+)\] | - )(?P<results>.*)')

    # XXX overwrite property
    success = 0

    def _parse(self, stream):
        for _, _, _, results in self.line_regex.findall(stream.read()):
            if results == "FAILED TO LOAD MODULE":
                self.errors += 1
            else:
                self.success += results.count('.')
                self.total += results.count('.')
                self.failures += results.count('F')
                self.total += results.count('F')
                self.errors += results.count('E')
                self.total += results.count('E')
                self.skipped += results.count('s')
                self.total += results.count('s')
        if self.failures or self.errors:
            self.set_status(FAILURE)
        elif self.skipped:
            self.set_status(PARTIAL)
        elif not self.success:
            self.set_status(NODATA)


class PyDotTestChecker(PyUnitTestChecker):
    """check that py.test based unit tests of a python package succeed

    spawn py.test and parse output (expect a standard TextTestRunner)
    """
    need_preprocessor = 'install'
    id = 'py.test'
    parsercls = PyDotTestParser
    parsed_content = 'stdout'
    options_def = PYVERSIONS_OPTIONS.copy()

    def get_command(self, command, python):
        # XXX coverage
        return ['py.test', '--exec=%s' % python, '--nomagic', '--tb=no'] + command

register('checker', PyDotTestChecker)


class PyLintChecker(BaseChecker):
    """check that the python package as a decent pylint evaluation
    """
    need_preprocessor = 'install'
    id = 'pylint'
    options_def = {
        'pylintrc': {
            'help': ('path to a pylint configuration file.'),
            },
        'pylint.threshold': {
            'type': 'int', 'default': 7,
            'help': ('integer between 1 and 10 telling expected pylint note to '
                     'pass this check. Default to 7.'),
         },
        'pylint.show_categories': {
            'type': 'csv', 'default': ['E', 'F'],
            'help': ('comma separated list of pylint message categories to add to '
                     'reports. Default to error (E) and failure (F).'),
         },
        'pylint.additional_builtins': {
            'type': 'csv',
            'help': ('comma separated list of additional builtins to give to '
                     'pylint.'),
            },
        'pylint.disable': {
            'type': 'csv',
            'help': ('comma separated list of pylint message id that should be '
                     'ignored.'),
            },
        'pylint.ignore': {
            'type': 'csv',
            'help': 'comma separated list of files or directories to ignore',
            },
        }

    def version_info(self):
        self.record_version_info('pylint', pylint_version)

    def do_check(self, test):
        """run the checker against <path> (usually a directory)"""
        # XXX should consider python version
        threshold = self.options.get('pylint.threshold')
        pylintrc_path = self.options.get('pylintrc')
        linter = PyLinter(pylintrc=pylintrc_path)
        # register checkers
        checkers.initialize(linter)
        # load configuration
        package_wd_path = test.project_path()
        if exists(join(package_wd_path, 'pylintrc')):
            linter.load_file_configuration(join(package_wd_path, 'pylintrc'))
        else:
            linter.load_file_configuration()
        linter.set_option('persistent', False)
        linter.set_option('reports', 0, action='store')
        linter.quiet = 1
        # set file or dir to ignore
        for option in ('ignore', 'additional_builtins', 'disable'):
            value = self.options.get('pylint.' + option)
            if value is not None:
                linter.global_set_option(option.replace('_', '-'), ','.join(value))
        # message categories to record
        categories = self.options.get('pylint.show_categories')
        linter.set_reporter(MyLintReporter(self.writer, test.tmpdir, categories))
        # run pylint
        linter.check(pyinstall_path(test))
        try:
            note = eval(linter.config.evaluation, {}, linter.stats)
            self.writer.raw('pylint.evaluation', '%.2f' % note, 'result')
        except ZeroDivisionError:
            self.writer.raw('pylint.evaluation', '0', 'result')
            note = 0
        except RESOURCE_LIMIT_EXCEPTION:
            raise
        except Exception:
            self.writer.error('Error while processing pylint evaluation',
                              path=test.project_path(subpath=True), tb=True)
            note = 0
        self.writer.raw('statements', '%i' % linter.stats['statement'], 'result')
        if note < threshold:
            return FAILURE
        return SUCCESS

try:
    from pylint import checkers
    from pylint.lint import PyLinter
    from pylint.__pkginfo__ import version as pylint_version
    from pylint.interfaces import IReporter
    from pylint.reporters import BaseReporter
    register('checker', PyLintChecker)

    class MyLintReporter(BaseReporter):
        """a partial pylint writer (implements only the message method, not
        methods necessary to display layouts
        """
        __implements__ = IReporter

        def __init__(self, writer, basepath, categories):
            self.writer = writer
            self.categories = set(categories)
            self._to_remove = len(basepath) + 1 # +1 for the leading "/"

        def add_message(self, msg_id, location, msg):
            """ manage message of different type and in the context of path """
            if not msg_id[0] in self.categories:
                return
            path, line = location[0], location[-1]
            path = path[self._to_remove:]
            if msg_id[0] == 'I':
                self.writer.info(msg, path=path, line=line)
            elif msg_id[0]  == 'E':
                self.writer.error(msg, path=path, line=line)
            elif msg_id[0] == 'F':
                self.writer.fatal(msg, path=path, line=line)
            else: # msg_id[0] in ('R', 'C', 'W')
                self.writer.warning(msg, path=path, line=line)

        def display_results(self, layout):
            pass
except ImportError, e:
    warn("unable to import pylint. Pylint checker disabled : %s" % e)


class PyCoverageChecker(BaseChecker):
    """retrieve the tests coverage data

    The coverage data are coming from the pyunit checker with the "pycoverage"
    configuration variable

    When devtools is available, test will be launched in a coverage mode. This
    test will gather coverage information, and will succeed if the test coverage
    is superior to a given threshold. *This checker must be executed after the
    python_unittest checker.
    """
    id = 'pycoverage'
    options_def = {
        'coverage.threshold': {
            'type': 'int', 'default': 80,
            'help': ('integer between 1 and 100 telling expected percent coverage '
                     'to pass this check. Default to 80.\n'
                     'PARTIAL returned when cover rate between threshold and threshold / 2.\n'
                     'ERROR returned when cover rate under threshold / 2'),
        },
        'coverage.data': {
            'required': True,
            'help': 'collect coverage data file',
        },
    }

    def version_info(self):
        if coverage:
            version = getoutput('%s --version' % COVERAGE_CMD).strip()
            self.record_version_info('python-coverage', version)

    def do_check(self, test):
        """run the checker against <path> (usually a directory)"""
        self.threshold = float(self.options.get('coverage.threshold')) / 100
        self.coverage_data = self.options.get('coverage.data')
        if not exists(self.coverage_data):
            self.writer.fatal('no coverage information', path=self.coverage_data)
            return NODATA
        line_rate, branch_rate = self._get_cover_info(test)
        # in case of error during coverage reporting
        if line_rate is None:
            return ERROR
        # global summary
        self.writer.raw('cover-line-rate', '%.3f' % line_rate, 'result')
        self.writer.raw('cover-branch-rate', '%.3f' % branch_rate, 'result')
        if line_rate < self.threshold:
            return FAILURE
        return SUCCESS

    def _get_log_method(self, pc_cover):
        if pc_cover < (self.threshold / 2):
            writer = self.writer.error
        elif pc_cover < self.threshold:
            writer = self.writer.warning
        else:
            writer = self.writer.info
        return writer

    def _get_cover_info(self, test):
        if coverage is None:
            raise Exception('install python-coverage')
        covertool = coverage.coverage()
        covertool.use_cache(self.coverage_data)
        covertool.load()
        try:
            report_file = join(test.project_path(), "coverage.xml")
            covertool.xml_report(outfile=report_file, ignore_errors=True)
            report = etree.parse(report_file).getroot()
            pc_cover = float(report.attrib.get('line-rate'))
            br_rate  = float(report.attrib.get('branch-rate'))
            # format of the xml_report file is compatible with Cobertura
            # <http://cobertura.sourceforge.net/>
            #
            # FIXME missing stats: <stat> / <miss>
            # FIXME p_name construction (arbitrary slice)
            for package in report.iter("package"):
                p_name = package.attrib.get('name')
                p_name = ".".join(p_name.split(".")[6:])
                # class *are* files in Coberture (from java world)
                for cls in package.iter("class"):
                    c_name = ".".join([p_name, cls.attrib.get('name')])
                    c_pc_cover = float(cls.attrib.get('line-rate'))
                    c_br_rate  = float(cls.attrib.get('branch-rate'))
                    logger = self._get_log_method(c_pc_cover)
                    logger("line rate: %3.0f %% / branch rate: %3.0f %%"
                           % (c_pc_cover*100, c_br_rate*100), path=c_name)
        except Exception, err:
            pc_cover = br_rate = None
            self.writer.fatal(err, tb=True)
        finally:
            return (pc_cover, br_rate)

if coverage is not None:
    register('checker', PyCoverageChecker)


class PyCheckerOutputParser(SimpleOutputParser):
    non_zero_status_code = FAILURE
    def parse_line(self, line):
        try:
            path, line, msg = line.split(':')
            self.writer.error(msg, path=path, line=line)
            self.status = FAILURE
        except ValueError:
            self.unparsed.append(line)

class PyCheckerChecker(BaseChecker):
    """check that unit tests of a python package succeed

    spawn unittest and parse output (expect a standard TextTestRunner)
    """
    id = 'pychecker'
    need_preprocessor = 'install'

    def do_check(self, test):
        """run the checker against <path> (usually a directory)"""
        command = ['pychecker', '-Qqe', 'Style']
        command += get_module_files(pyinstall_path(test))
        return ParsedCommand(self.writer, command, parsercls=PyCheckerOutputParser).run()

    def version_info(self):
        self.record_version_info('pychecker', getoutput("pychecker --version").strip())

register('checker', PyCheckerChecker)

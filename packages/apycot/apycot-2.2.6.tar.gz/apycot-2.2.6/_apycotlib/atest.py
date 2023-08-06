"""APyCoT task / test

A task is a queue (pending) test

A test defines :
* a unit of sources to test (a project)
* a list of checks to apply to this unit
* how to build the test environment (preprocessing, dependencies...)
"""
from __future__ import with_statement

__docformat__ = "restructuredtext en"

import os
import os.path
import sys
import tempfile
from shutil import rmtree

from logilab.common.proc import ResourceError

from cubes.apycot.__pkginfo__ import version as apycot_version

from apycotlib import (ConfigError, Command, get_registered,
                       SUCCESS, SKIPPED, ERROR, KILLED)


def substitute(value, substitutions):
    if hasattr(value, 'replace') and value:
        for key, val in substitutions.iteritems():
            value = value.replace('${%s}' % key, val)
    return value

def substitute_dict(dict, substitutions):
    for key, value in dict.iteritems():
        dict[key] = substitute(value, substitutions)
    return dict

def clean_path(path):
    """remove trailing path separator from path"""
    if path and path[-1] == os.sep:
        return path[:-1]
    return path

def update_path(old_path, new_path):
    """update sys.path"""
    if old_path is not None:
        for path in old_path.split(os.pathsep):
            try:
                sys.path.remove(clean_path(path))
            except ValueError:
                continue
    if new_path is not None:
        new_path = new_path.split(os.pathsep)
        new_path.reverse()
        for path in new_path:
            sys.path.insert(0, clean_path(path))



class Test(object):
    """the single source unit test class"""

    def __init__(self, texec, writer, options):
        # directory where the test environment will be built
        self.tmpdir = tempfile.mkdtemp(dir=options.get('test_dir'))
        # notify some subprocesses they're executed by apycot through an
        # environment variable
        os.environ['APYCOT_ROOT'] = self.tmpdir
        # test config / tested project environment
        self.tconfig = texec.configuration
        self.environment = texec.environment
        self.branch = texec.branch
        # IWriter object
        self.writer = writer
        # local caches
        self._configs = {}
        self._repositories = {}
        # environment variables as a dictionary
        self.environ = self.tconfig.apycot_process_environment()
        self.environ.update(self.environment.apycot_process_environment())
        self.environ.setdefault('LC_ALL', 'fr_FR.UTF-8') # XXX force utf-8
        self._substitute(self.environment, self.environ)
        # Track environment change to be able to restore it later.
        # Notice sys.path is synchronized with the PYTHONPATH environment variable
        self._tracks = {}
        # flag indicating whether to clean test environment after test execution
        # or if an archive containing it should be uploaded
        self.keep_test_dir = options.get('keep_test_dir', False)
        self.archive = options.get('archive', False)
        # set of preprocessors which have failed
        self._failed_pp = set()
        self.executed_checkers = {}
        self.global_status = SUCCESS
        os.umask(022)

    def __str__(self):
        return repr(self.apycot_repository())

    def _substitute(self, pe, configdict):
        substitute_dict(configdict,
                        {'NAME': pe.name, 'TESTDIR': self.tmpdir,
                         'SRCDIR': self.apycot_repository(pe).co_path})

    # resource accessors #######################################################

    def apycot_config(self, pe=None):
        if pe is None:
            pe = self.environment
        try:
            return self._configs[pe.eid]
        except KeyError:
            config = self.tconfig.apycot_configuration(pe)
            self._configs[pe.eid] = config
            self._substitute(pe, config)
            return config

    def apycot_repository(self, pe=None):
        if pe is None:
            pe = self.environment
        try:
            return self._repositories[pe.eid]
        except KeyError:
            from apycotlib.repositories import get_repository
            repdef = {'repository': pe.repository,
                      'path': pe.vcs_path,
                      'branch': self.branch}
            # don't overwrite branch hardcoded on the environment: have to be
            # done here, not only in when starting plan (eg in entities.py)
            # since project env may not be the tested project env
            pecfg = pe.apycot_configuration()
            if pecfg.get('branch'):
                repdef['branch'] = pecfg['branch']
            apyrep = get_repository(repdef)
            self._repositories[pe.eid] = apyrep
            return apyrep

    def project_path(self, subpath=False):
        path = self.apycot_repository().co_path
        if subpath and self.apycot_config().get('subpath'):
            return os.path.join(path, self.apycot_config()['subpath'])
        return path

    # test initialisation / cleanup ############################################

    def setup(self):
        """setup the test environment"""
        self.writer.start()
        self.writer.raw('apycot', apycot_version, 'version')
        # setup environment variables
        if self.environ:
            for key, val in self.environ.iteritems():
                self.update_env(self.tconfig.name, key, val)

    def clean(self):
        """clean the test environment"""
        try:
            self.writer.end(self.global_status, self.archive and self.tmpdir)
        except:
            # XXX log error
            pass
        if not self.keep_test_dir:
            rmtree(self.tmpdir)
        else:
            self.writer.execution_info('temporary directory not removed: %s',
                                       self.tmpdir)

    # environment tracking #####################################################

    def update_env(self, key, envvar, value, separator=None):
        """update an environment variable"""
        envvar = envvar.upper()
        orig_value = os.environ.get(envvar)
        if orig_value is None:
            orig_value = ''
        uid = self._make_key(key, envvar)
        assert not self._tracks.has_key(uid)
        if separator is not None:
            if orig_value:
                orig_values = orig_value.split(separator)
            else:
                orig_values = [] # don't want a list with an empty string
            if not value in orig_values:
                orig_values.insert(0, value)
                self._set_env(uid, envvar, separator.join(orig_values))
        elif orig_value != value:
            self._set_env(uid, envvar, value)

    def clean_env(self, key, envvar):
        """reinitialize an environment variable"""
        envvar = envvar.upper()
        uid = self._make_key(key, envvar)
        if self._tracks.has_key(uid):
            orig_value = self._tracks[uid]
            if envvar == 'PYTHONPATH':
                update_path(os.environ.get(envvar), orig_value)
            if self.writer:
                self.writer.debug('Reset %s=%r', envvar, orig_value)
            if orig_value is None:
                del os.environ[envvar]
            else:
                os.environ[envvar] = self._tracks[uid]
            del self._tracks[uid]

    def _make_key(self, key, envvar):
        """build a key for an environment variable"""
        return '%s-%s' % (key, envvar)

    def _set_env(self, uid, envvar, value):
        """set a new value for an environment variable
        """
        if self.writer:
            self.writer.debug('Set %s=%r', envvar, value)
        orig_value = os.environ.get(envvar)
        self._tracks[uid] = orig_value
        os.environ[envvar]  = value
        if envvar == 'PYTHONPATH':
            update_path(orig_value, value)

    # api to call a particular preprocessor / checker #########################

    def checkout(self, pe):
        vcsrepo = self.apycot_repository(pe)
        cocmd = vcsrepo.co_command()
        if cocmd:
            Command(self.writer, cocmd, raises=True, shell=True,
                    cwd=self.tmpdir).run()
        movebranchcmd = vcsrepo.co_move_to_branch_command()
        if movebranchcmd:
            Command(self.writer, movebranchcmd, shell=True,
                    cwd=self.tmpdir).run()
        self.writer.link_to_revision(pe, vcsrepo)
        self.writer.refresh_log(True)

    def call_preprocessor(self, pptype, penv):
        cfg = self.apycot_config(penv)
        ppid = cfg.get(pptype)
        if ppid is not None:
            # fetch preprocessors options set on the project environment
            preprocessor = get_registered('preprocessor', ppid)(self.writer, cfg)
        else:
            # XXX log?
            return
        path = self.apycot_repository(penv).co_path
        dependency = path != self.project_path()
        msg = 'running preprocessor %(pp)s to perform %(pptype)s'
        msg_data = {'pptype': pptype,
                    'pp': preprocessor.id,}
        if dependency:
            msg + ' on dependency %(pe)s'
            msg_data['pe'] = penv.name
        self.writer.info(msg % msg_data, path=path)
        try:
            preprocessor.run(self, path)
        except Exception, ex:
            msg = '%s while running preprocessor %s: %s'
            self.writer.fatal(msg, ex.__class__.__name__, preprocessor.id, ex,
                              path=path, tb=True)
            self._failed_pp.add(pptype)

    def run_checker(self, id, options=None, nonexecuted=False):
        """run all checks in the test environment"""
        if options is None:
            options = {}
        else:
            self._substitute(self.environment, options)
        check_writer = self.writer.make_check_writer()
        if nonexecuted:
            check_writer.start(id)
            check_writer.end(SKIPPED)
            return None, SKIPPED # XXX
        checker = get_registered('checker', id)(check_writer, options)
        check_writer.start(checker)
        if checker.need_preprocessor in self._failed_pp:
            msg = 'Can\'t run checker %s: preprocessor %s have failed'
            check_writer.fatal(msg, checker.id, checker.need_preprocessor)
            check_writer.end(SKIPPED)
            return checker, SKIPPED # XXX
        try:
            checker.check_options()
            status = checker.check(self)
            self.executed_checkers[checker.id] = status
        except ConfigError, ex:
            msg = 'Config error for %s checker: %s'
            check_writer.fatal(msg, checker.id, ex)
            status = ERROR
        except ResourceError, ex:
            check_writer.fatal('%s resource limit reached, aborted', ex.limit)
            status = KILLED
            raise
        except MemoryError:
            check_writer.fatal('memory resource limit reached, arborted')
            status = KILLED
            raise
        except Exception, ex:
            msg = 'Error while running checker %s: %s'
            check_writer.fatal(msg, checker.id, ex, tb=True)
            status = ERROR
        finally:
            check_writer.end(status)
            #globstatus = min(globstatus, status)
            self.writer.execution_info('%s [%s]', checker.id, status)
            with self.writer._lock:
                self.global_status = min(self.global_status, status)
        return checker, status

"""installation preprocessor using distutils setup.py

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
from __future__ import with_statement

__docformat__ = "restructuredtext en"

import os
import shutil
import sys
from os.path import join, exists, abspath, dirname
from glob import glob

from logilab.common.textutils import splitstrip
from logilab.common.decorators import cached

from apycotlib import register, SetupException
from apycotlib import Command
from apycotlib.preprocessors import BasePreProcessor

def pyversion_available(python):
    return not os.system('%s -V 2>/dev/null' % python)

@cached
def pyversions(test):
    config = test.apycot_config()
    tested_pyversions = config.get('tested_python_versions')
    if tested_pyversions:
        pyversions = set(splitstrip(tested_pyversions))
    elif config.get('use_pkginfo_python_versions'):
        from logilab.devtools.lib.pkginfo import PackageInfo
        try:
            pkginfodir = dirname(test.environ['pkginfo'])
        except KeyError:
            pkginfodir = test.project_path()
        try:
            pkginfo = PackageInfo(directory=pkginfodir)
            pyversions = set(pkginfo.pyversions)
        except (NameError, ImportError):
            pyversions = set()
        ignored_pyversions = config.get('ignored_python_versions')
        if ignored_pyversions:
            ignored_pyversions = set(ignored_pyversions)
            ignored_pyversions = pyversions.intersection(
                ignored_pyversions)
            if ignored_pyversions:
                for py_ver in ignored_pyversions:
                    test.writer.debug('python version %s ignored', py_ver)
                pyversions.difference_update(ignored_pyversions)
    else:
        pyversions = None
    if pyversions:
        pyversions_ = []
        for pyver in pyversions:
            python = 'python%s' % pyver
            if not pyversion_available(python):
                test.writer.error(
                    'config asked for %s, but it\'s not available', pyver)
            else:
                pyversions_.append(python)
        pyversions = pyversions_
    else:
        pyversions = [sys.executable]
    return pyversions

INSTALL_PREFIX = {}

class DistutilsProcessor(BasePreProcessor):
    """python setup.py pre-processor

       Use a distutils'setup.py script to install a Python package. The
       setup.py should provide an "install" function which run the setup and
       return a "dist" object (i.e. the object return by the distutils.setup
       function). This preprocessor may modify the PATH and PYTHONPATH
       environment variables.
    """
    id = 'python_setup'
    _python_path_set = None

    options_def = {
        'verbose': {
            'type': 'int', 'default': False,
            'help': 'set verbose mode'
            },
        }

    # PreProcessor interface ##################################################

    def run(self, test, path=None):
        """run the distutils setup.py install method on a path if
        the path is not yet installed
        """
        if path is None:
            path = test.project_path()
        if not DistutilsProcessor._python_path_set:
            path = test.project_path()
            py_lib_dir = join(test.tmpdir, 'local', 'lib', 'python')
            # setuptools need this directory to exists
            if not exists(py_lib_dir):
                os.makedirs(py_lib_dir)
            test.update_env(path, 'PYTHONPATH', py_lib_dir, os.pathsep)
            test.update_env(path, 'PATH', join(test.tmpdir, 'local', 'bin'),
                            os.pathsep)
            DistutilsProcessor._python_path_set = py_lib_dir
            sitecustomize = open(join(py_lib_dir, 'sitecustomize.py'), 'w')
            sitecustomize.write('''import sys, os.path as osp
sys.path.insert(0, osp.join(%r, "python%%s.%%s" %% sys.version_info[:2], "site-packages"))
''' % join(test.tmpdir, 'local', 'lib'))
            sitecustomize.close()
        # cache to avoid multiple installation of the same module
        if path in INSTALL_PREFIX:
            return
        if not exists(join(path, 'setup.py')):
            raise SetupException('No file %s' % abspath(join(path, 'setup.py')))
        # XXX need better detection of C extension
        if glob(join(path, '*.c')) or glob(join(path, '*.cpp')):
            pythons = pyversions(test) or [sys.executable]
            installopt = '--prefix'
            INSTALL_PREFIX[path] = join(test.tmpdir, 'local', 'lib', pythons[0])
        else:
            pythons = (pyversions(test) or [sys.executable])[0],
            installopt = '--home'
            INSTALL_PREFIX[path] = join(test.tmpdir, 'local', 'lib', 'python')
        for python in pythons:
            cmdargs = [python, 'setup.py', 'install', installopt,
                       join(test.tmpdir, 'local')]
            if not self.options.get('verbose'):
                cmdargs.append('--quiet')
            cmd = Command(self.writer, cmdargs, raises=True, cwd=path)
            cmd.run()
        if exists(join(path, 'build')):
            shutil.rmtree(join(path, 'build')) # remove the build directory


register('preprocessor', DistutilsProcessor)

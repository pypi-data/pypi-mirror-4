"""Writer sending data to a cubicweb instance which store it and may be used
to display reports

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
from __future__ import with_statement
__docformat__ = "restructuredtext en"

import os
import logging
import tarfile
import tempfile
import traceback
from datetime import datetime
from StringIO import StringIO
from threading import RLock

from logilab.mtconverter import xml_escape

from cubicweb import Binary

REVERSE_SEVERITIES = {
    logging.DEBUG :   u'DEBUG',
    logging.INFO :    u'INFO',
    logging.WARNING : u'WARNING',
    logging.ERROR :   u'ERROR',
    logging.FATAL :   u'FATAL'
    }

ARCHIVE_EXT = '.tar.bz2'
ARCHIVE_MODE = 'w:bz2'
ARCHIVE_NAME = "apycot-archive-%(instance-id)s-%(exec-id)s"+ARCHIVE_EXT

def make_archive_name(cwinstid, execution_id):
    # replace ':' as tar use them to fetch archive over network
    exec_data = {'exec-id':     execution_id,
                 'instance-id': cwinstid,
                }
    return (ARCHIVE_NAME % exec_data).replace(':', '.')



class AbstractLogWriter(object):

    def _unicode(self, something):
        if isinstance(something, str):
            return unicode(something, 'utf-8', 'replace')
        if not isinstance(something, unicode):
            return unicode(something)
        return something

    def debug(self, *args, **kwargs):
        """log an debug"""
        self.log(logging.DEBUG, *args, **kwargs)

    def info(self, *args, **kwargs):
        """log an info"""
        self.log(logging.INFO, *args, **kwargs)

    def warning(self, *args, **kwargs):
        """log a warning"""
        self.log(logging.WARNING, *args, **kwargs)

    def error(self, *args, **kwargs):
        """log an error"""
        self.log(logging.ERROR, *args, **kwargs)

    def fatal(self, *args, **kwargs):
        """log a fatal error"""
        self.log(logging.FATAL, *args, **kwargs)

    critical = fatal

    def _msg_info(self, *args, **kwargs):
        path = kwargs.pop('path', None)
        line = kwargs.pop('line', None)
        tb = kwargs.pop('tb', False)
        assert not kwargs
        if len(args) > 1:
            args = [self._unicode(string) for string in args]
            msg = args[0] % tuple(args[1:])
        else:
            assert args
            msg = self._unicode(args[0])
        if tb:
            stream = StringIO()
            traceback.print_exc(file=stream)
            msg += '\n' + stream.getvalue()
        return path, line, msg

    def log(self, severity, *args, **kwargs):
        """log a message of a given severity"""
        path, line, msg = self._msg_info(*args, **kwargs)
        self._log(severity, path, line, msg)

    def _log(self, severity, path, line, msg):
        raise NotImplementedError()


class BaseDataWriter(AbstractLogWriter):
    """print execution message on stderr and store Test execution data to
    a CubicWeb instance (using the apycot cube)
    """

    def __init__(self, cnxh, target_eid):
        self._cnxh = cnxh
        # eid of the execution entity
        self._eid = target_eid
        self._logs = []
        self._logs_sent = 0
        self._lock = RLock()

    def start(self):
        pass

    def end(self):
        pass

    def set_exec_status(self, status):
        with self._lock:
            self._cnxh.execute(
                'SET X status %(status)s WHERE X eid %(x)s',
                {'status': status, 'x': self._eid})
            self._cnxh.commit()

    def execution_info(self, *args, **kwargs):
        msg = self._msg_info(*args, **kwargs)[-1]
        if isinstance(msg, unicode):
            msg = msg.encode('utf-8')
        print msg

    def _log(self, severity, path, line, msg):
        encodedmsg = u'%s\t%s\t%s\t%s<br/>' % (severity, path or u'',
                                               line or u'', xml_escape(msg))
        self._logs.append(encodedmsg)

    def raw(self, name, value, type=None, commit=True):
        """give some raw data"""
        with self._lock:
            self._cnxh.cw.create_entity(
                'CheckResultInfo', label=self._unicode(name),
                value=self._unicode(value), type=type and unicode(type),
                for_check=self._cnxh.cw.entity_from_eid(self._eid))
            if commit:
                self._cnxh.commit()

    def refresh_log(self, flush=True):
        log = self._logs
        with self._lock:
            if self._logs_sent < len(log):
                self._cnxh.execute(
                    'SET X log %(log)s WHERE X eid %(x)s',
                    {'log': u'\n'.join(log), 'x': self._eid})
                self._log_sent = len(log)
            if flush:
                self._cnxh.commit()


class CheckDataWriter(BaseDataWriter):
    """Writer intended to report Check level log and result."""

    def start(self, checker):
        """Register the given checker as started"""
        with self._lock:
            crname = getattr(checker, 'id', checker) # may be the checked id
            self._eid = self._cnxh.cw.create_entity(
                'CheckResult', name=self._unicode(crname), status=u'processing',
                starttime=datetime.now(),
                during_execution=self._cnxh.cw.entity_from_eid(self._eid)).eid
            if hasattr(checker, 'options'):
                options = ['%s=%s' % (k, v) for k, v in checker.options.iteritems()
                           if k in checker.options_def
                           and v != checker.options_def[k].get('default')]
                if options:
                    self.info('\n'.join(options))
                    self.refresh_log(flush=False)
            self._cnxh.commit()

    def end(self, status):
        """Register the given checker as closed with status <status>"""
        with self._lock:
            """end of the latest started check"""
            self._cnxh.execute(
                'SET X status %(status)s, X endtime %(endtime)s, X log %(log)s '
                'WHERE X eid %(x)s',
                {'status': self._unicode(status), 'endtime': datetime.now(),
                 'log': u'\n'.join(self._logs), 'x': self._eid})
            self._cnxh.commit()


class TestDataWriter(BaseDataWriter):
    """Writer intended to report Test level log and result."""

    def make_check_writer(self):
        """Return a CheckDataWriter suitable to write checker log and result within this test"""
        self.refresh_log()
        return CheckDataWriter(self._cnxh, self._eid)

    def link_to_revision(self, environment, vcsrepo):
        changeset = vcsrepo.changeset()
        if changeset is not None:
            if not self._cnxh.execute(
                'SET X using_revision REV '
                'WHERE X eid %(x)s, REV changeset %(cs)s, '
                'REV from_repository R, R eid %(r)s',
                {'x': self._eid, 'cs': changeset,
                 'r': environment.repository.eid}):
                self.raw(repr(vcsrepo), changeset, 'revision')

    def start(self):
        self.set_exec_status(u'set up')

    def end(self, status, archivedir=None):
        """mark the current test as closed (with status <status>) and archive if requested."""
        with self._lock:
            """end of the test execution"""
            if self._logs_sent < len(self._logs):
                self._cnxh.execute('SET X status %(status)s, X log %(log)s WHERE X eid %(x)s',
                                   {'log': u'\n'.join(self._logs),
                                    'status': self._unicode(status),
                                    'x': self._eid})
            else:
                self._cnxh.execute('SET X status %(status)s WHERE X eid %(x)s',
                                   {'status': self._unicode(status),
                                    'x': self._eid})
            self._cnxh.commit()
            if archivedir:
                archive = make_archive_name(self._cnxh.cwinstid, self._eid)
                archivefpath = os.path.join(tempfile.gettempdir(), archive)
                tarball = tarfile.open(archivefpath, ARCHIVE_MODE)
                try:
                    tarball.add(archivedir)
                    tarball.close()
                    self._cnxh.cw.create_entity(
                        'File', data=Binary(open(archivefpath, 'rb').read()),
                        data_format=u'application/x-bzip2',
                        data_name=unicode(archive),
                        reverse_log_file=self._cnxh.cw.entity_from_eid(self._eid))
                except:
                    self.error('while archiving execution directory', tb=True)
                finally:
                    os.unlink(archivefpath)
                self._cnxh.commit()


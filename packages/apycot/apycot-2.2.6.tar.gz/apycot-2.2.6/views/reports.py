"""this module contains some synthetics report views for test execution results

:organization: Logilab
:copyright: 2009-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.common.ureports import HTMLWriter, Table, Span, Link, Text
from logilab.common.decorators import cached
from logilab.mtconverter import xml_escape

from StringIO import StringIO

from cubicweb.uilib import domid
from cubicweb.view import EntityView
from cubicweb.selectors import is_instance

from cubes.narval.views import no_robot_index


@cached
def all_check_results(tconfig):
    rset = tconfig._cw.execute('Any MAX(X), XN GROUPBY XN, EXB ORDERBY XN '
                               'WHERE X is CheckResult, X name XN, '
                               'X during_execution EX, EX using_config C, '
                               'EX branch EXB, C eid %(c)s',
                               {'c': tconfig.eid})
    return list(rset.entities())

def latest_check_result_by_name(tconfig, name, branch):
    for cr in all_check_results(tconfig):
        if cr.name == name and cr.execution.branch == branch:
            return cr


class ProjectEnvironmentLatestExecutionSummary(EntityView):
    __regid__ = 'summary'
    __select__ = is_instance('ProjectEnvironment')
    title = _('Test executions summary')

    html_headers = no_robot_index

    def call(self, title=None):
        configs = []
        map(configs.extend, (e.reverse_use_environment for e in self.cw_rset.entities()))
        self.multiple_configs_report(configs, title, incontext=True)

    def cell_call(self, row, col, title=None):
        entity = self.cw_rset.get_entity(row, col)
        self.multiple_configs_report(entity.reverse_use_environment,
                                     title, incontext=True)

    def multiple_configs_report(self, configs, title, incontext):
        self.w(u'<div class="section">')
        self.w(u'<h3>%s</h3>\n' % (title or self._cw._(self.title)))
        if not configs:
            self.w(self._cw._('no test execution results to display'))
        else:
            self._cw.add_css('cubes.apycot.css')
            self.w(multiple_configs_table(self._cw._, configs,
                                          incontext=incontext))
        self.w(u'</div>')


class TestConfigLatestExecutionSummary(ProjectEnvironmentLatestExecutionSummary):
    __select__ = is_instance('TestConfig',)

    html_headers = no_robot_index

    def call(self, title=None):
        self.multiple_configs_report(list(self.cw_rset.entities()),
                                     title, incontext=False)

    def cell_call(self, row, col, title=None):
        self.multiple_configs_report([self.cw_rset.get_entity(row, col)],
                                      title, incontext=False)


class TestExecutionSummary(EntityView):
    __select__ = is_instance('TestExecution',)
    __regid__ = 'summary'

    html_headers = no_robot_index

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self._cw.add_css('cubes.apycot.css')
        self.w(u'<table class="summary">')
        self.w(u'<tr><th>%s</th><th>%s</th></tr>'
               % (self._cw._('name'), self._cw._('status')))
        for checkname in entity.configuration.all_checks():
            check = entity.check_result_by_name(checkname)
            if check is None:
                status = 'nc'
                url = entity.absolute_url()
            else:
                status = entity.check_result_by_name(checkname).status
                url = check.absolute_url()
            self.w(u'<tr><td><a href="%s">%s</a></td><td class="status_%s">%s</td></tr>'
                   % (url, xml_escape(checkname), status, status))
        self.w(u'</table>')


def multiple_configs_table(_, configs, incontext=False):
    """return a synthetic reports table for multiple configurations executions
    """
    branches = {}
    allchecks = set()
    for conf in configs:
        for cr in all_check_results(conf):
            allchecks.add(cr.name)
            branches.setdefault(conf, set()).add(cr.execution.branch)
    allchecks = sorted(allchecks)
    table = Table(cols=2+len(allchecks), klass='apycotreport',
                  cheaders=2, rheaders=1, rrheaders=len(configs) > 5)
    # headers
    table.append(Text(_('name')))
    table.append(Text(_('branch')))
    for check_name in allchecks:
        table.append(Text(check_name.replace('_', ' ')))
    # table content
    for conf in configs:
        first_branch = True
        if incontext:
            conf_title = conf.printable_value('name')
        else:
            conf_title = xml_escape(conf.dc_title())
        for branch in sorted(branches.get(conf, ())):
            if first_branch:
                link = Link(xml_escape(conf.absolute_url()),
                            '%s' % (conf_title,),
                            klass='apycot_title')
                table.append(Span((link,), klass='apycot_testname'))
            else:
                table.append(Span(u' '))
            first_branch = False
            link = Link(xml_escape(conf.absolute_url()),
                        '%s' % (xml_escape(branch or 'default'),),
                        klass='apycot_title')
            table.append(Span((link,), klass='apycot_branchname'))
            for column in allchecks:
                checkresult = latest_check_result_by_name(conf, column, branch)
                if checkresult:
                    status = checkresult.status
                    url = checkresult.execution.absolute_url(tab=column)
                    title = Link(xml_escape(url), _(status), klass='apycot_title')
                else:
                    title = _('nc')
                    status = 'nc'
                table.append(Span((title,), klass='status_%s' % status))
    # recall table headers
    if len(configs) > 5:
        table.append(Text(_('name')))
        table.append(Text(_('branch')))
        for check_name in allchecks:
            table.append(Text(check_name.replace('_', ' ')))
    # dump html and return results
    stream = StringIO()
    writer = HTMLWriter(snippet=True)
    writer.format(table, stream, 'unicode')
    return stream.getvalue()

"""this module contains the primary views for apycot entities

:organization: Logilab
:copyright: 2008-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"
_ = unicode

from datetime import datetime

from logilab.mtconverter import xml_escape

from cubicweb import Unauthorized, tags
from cubicweb.selectors import is_instance, none_rset, score_entity
from cubicweb.view import EntityView
from cubicweb.web import uicfg, box
from cubicweb.web.views import tabs, tableview, baseviews
from cubicweb.web.views import ibreadcrumbs, idownloadable, navigation

from cubes.narval.views import no_robot_index

from cubes.narval.views.plan import PlanOptionsCell


_pvs = uicfg.primaryview_section
_pvdc = uicfg.primaryview_display_ctrl

class InfoLogMixin(object):

    def display_info_section(self, entity):
        rset = self._cw.execute(
            'Any X,T,L,V ORDERBY T,L WHERE X is CheckResultInfo, '
            'X type T, X label L, X value V, X for_check AE, AE eid %(ae)s',
            {'ae': entity.eid})
        title = self._cw._('execution information')
        self.wview('table', rset, 'null', title=title, displaycols=range(1, 4),
                   divid='info%s'%entity.eid)


class ChecksDescriptorMixin(object):
    def describe_execution(self, exc, changes_only=False, xml_compat=False):
        self._cw.add_css('cubes.apycot.css')
        _ = self._cw._
        if xml_compat:
            w = lambda x: self.w(xml_escape(x))
        else:
            w = self.w
        if not changes_only:
            if exc.endtime is not None:
                nb_checkers = len(exc.checkers)
                if exc.starttime:
                    duration = exc.endtime - exc.starttime
                else:
                    duration = self._cw._('unknown duration')
                if nb_checkers > 1:
                    w(u'<p>')
                    w(_(u'%(nb)s checkers run in %(dur)s')
                           % {'nb': nb_checkers, 'dur': duration})
                    w(u'</p>')
                else:
                    w(u'<p>')
                    w(_(u'%(nb)s checker run in %(dur)s')
                           % {u'nb': nb_checkers, 'dur': duration})
                    w(u'</p>')
            else:
                w(u'<p>')
                if exc.starttime:
                    duration = datetime.now() - exc.starttime
                else:
                    duration = self._cw._('unknown duration')
                w(_(u'running for %(dur)s') % {'dur': duration})
                w(u'</p>')
        changes = exc.status_changes()
        if changes_only:
            if changes:
                checkers = (new for old, new in changes.values())
            else:
                checkers = ()
                w(_(u'nothing changed'))
        else:
            checkers = exc.checkers
        if checkers:
            w(u'<dl>')
            for checker in checkers:
                w(u'<dt>%s</dt>' % xml_escape(checker.name))
                status = checker.view(u'incontext')
                if changes_only or (changes is not None and checker.name in changes):
                    old_status = changes[checker.name][0].view(u'incontext')
                    w(u'<dd><strong>%s</strong> (previously <strike><em>%s</em></strike>)</dd>'
                      % (status, old_status))
                else:
                    w(u'<dd><strong>%s</strong></dd>' % status)
            w(u'</dl>')


# TestExecution ################################################################

class TESummaryTable(EntityView):
    __regid__ = 'apycot.te.summarytable'
    __select__ = is_instance('TestExecution') | none_rset()
    title = _('Apycot executions')
    category = 'startupview'

    html_headers = no_robot_index
    default_rql = ('Any T,PE,TC,T,TB,TST,TET,TF, TS ORDERBY TST DESC WHERE '
                   'T status TS, T using_config TC, T using_environment PE, '
                   'T branch TB, T starttime TST, T endtime TET, T log_file TF?')

    def call(self):
        w = self.w
        req = self._cw
        if self.cw_rset is None:
            self.cw_rset = req.execute(self.default_rql)
        self.wview('apycot.te.table', self.cw_rset, 'null')


class TETable(tableview.EntityTableView):
    __regid__ = 'apycot.te.table'
    __select__ = is_instance('TestExecution')

    columns = ['testexecution', 'projectenvironment', 'using_config', 'checks', 'branch', 'starttime', 'endtime', 'log_file']
    column_renderers = {
            'testexecution': tableview.MainEntityColRenderer(
                vid='apycot.te.statuscell'),
            'using_config': tableview.RelatedEntityColRenderer(
                header=_('TestConfig'), getrelated=lambda x: x.configuration),
            'projectenvironment': tableview.RelatedEntityColRenderer(
                header=_('ProjectEnvironment'), getrelated=lambda x: x.environment),
            'checks': tableview.MainEntityColRenderer(
                header=_('checks'), addcount=False, vid='apycot.te.summarycell'),
            'log_file': tableview.RelationColRenderer(
                subvid='icon')
            }
    layout_args = {
            'display_filter': 'top'
            }

    def call(self, columns=None):
        self._cw.add_css('cubes.apycot.css')
        super(TETable, self).call(columns)


class TENoPETable(TETable):
    __regid__ = 'apycot.te.nopetable'
    columns = ['testexecution', 'using_config', 'checks', 'branch', 'starttime', 'endtime', 'log_file']


class TENoTCTable(TETable):
    __regid__ = 'apycot.te.notctable'
    columns = ['testexecution', 'projectenvironment', 'checks', 'branch', 'starttime', 'endtime', 'log_file']


_pvdc.tag_attribute(('TestExecution', 'priority',), {'vid': 'tasksqueue.priority'}) # XXX rtag inheritance bug
_pvs.tag_attribute(('TestExecution', 'execution_log'), 'relations')
_pvdc.tag_attribute(('TestExecution', 'execution_log'), {'vid': 'narval.formated_log',
                                                         'loglevel': 'Error'})
_pvs.tag_attribute(('TestExecution', 'log'), 'relations')
_pvdc.tag_attribute(('TestExecution', 'log'), {'vid': 'narval.formated_log'})
_pvs.tag_subject_of(('TestExecution', 'using_revision', '*'), 'hidden')
_pvs.tag_subject_of(('TestExecution', 'using_config', '*'), 'hidden')
_pvs.tag_subject_of(('TestExecution', 'log_file', '*'), 'hidden')
_pvs.tag_subject_of(('TestExecution', 'execution_of', '*'), 'hidden')
_pvs.tag_object_of(('*', 'during_execution', 'TestExecution'), 'hidden')


class TEPrimaryView(tabs.TabbedPrimaryView):
    __select__ = is_instance('TestExecution')

    default_tab = 'apycot.te.tab_setup'

    html_headers = no_robot_index

    @property
    def tabs(self):
        tabs = ['apycot.te.tab_setup']
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        for check in entity.reverse_during_execution:#configuration.all_checks:
            label = u'%s [<b class="status_%s">%s</b>]' % (
                xml_escape(check.name), check.status, self._cw._(check.status))
            tabs.append((check.anchored_name,
                         {'vid': 'apycot.te.checkresult', 'label': label,
                          'rset': check.as_rset()}))
        return tabs

    def render_entity_title(self, entity):
        self._cw.add_css('cubes.apycot.css')
        title = self._cw._('Execution of %(pe)s/%(config)s#%(branch)s') % {
            'config': entity.configuration.view('outofcontext'),
            'pe':     entity.environment.view('outofcontext'),
            'branch': entity.branch and xml_escape(entity.branch)}
        self.w('<h1>%s</h1>' % title)


class TEConfigTab(InfoLogMixin, tabs.PrimaryTab):
    __regid__ = _('apycot.te.tab_setup')
    __select__ = is_instance('TestExecution')

    html_headers = no_robot_index

    def display_version_configuration(self, entity):
        title = self._cw._('version configuration')
        try:
            rset = self._cw.execute(
                'Any R, REV, B ORDERBY RN '
                'WHERE TE using_revision REV, TE eid %(te)s, '
                'REV from_repository R, REV branch B, R source_url RN',
                {'te': entity.eid})
        except Unauthorized:
            return # user can't read repositories for instance
        self.wview('table', rset, 'null', title=title, divid='vc%s'%entity.eid)

    def render_entity_relations(self, entity):
        self.display_version_configuration(entity)
        self.display_info_section(entity)
        super(TEConfigTab, self).render_entity_relations(entity)


class TECheckResultsTab(InfoLogMixin, tabs.PrimaryTab):
    __regid__ = 'apycot.te.checkresult'
    __select__ = is_instance('CheckResult')

    html_headers = no_robot_index

    def render_entity_relations(self, entity):
        self.display_info_section(entity)
        super(TECheckResultsTab, self).render_entity_relations(entity)


class TEBreadCrumbTextView(ibreadcrumbs.BreadCrumbTextView):
    __select__ = is_instance('TestExecution')
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(entity.printable_value('starttime'))


class TEStatusCell(tabs.PrimaryTab):
    __select__ = is_instance('TestExecution')
    __regid__ = 'apycot.te.statuscell'
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(tags.a(self._cw._(entity.status), href=entity.absolute_url(),
                      klass="global status_%s" % entity.status,
                      title=self._cw._('see detailed execution report')))

class TESummaryCell(tabs.PrimaryTab):
    __select__ = is_instance('TestExecution')
    __regid__ = 'apycot.te.summarycell'
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        checks = []
        for check in entity.reverse_during_execution:
            content = u'%s (%s)' % (self._cw._(check.name), check.status)
            url = check.absolute_url()
            title = self._cw._('see execution report for %s') % check.name
            checks.append(tags.a(content, href=url, title=title))
        if checks:
            self.w(u', '.join(checks))


class TEOptionsCell(PlanOptionsCell):
    __select__ = PlanOptionsCell.__select__ & is_instance('TestExecution')

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        self.w(self._cw._(u'branch="%s"<br/>') % xml_escape(entity.branch))
        if entity.options:
            self.w(u'; ')
            self.w(xml_escape(u'; '.join(entity.options.splitlines())))


class TEDescriptionView(ChecksDescriptorMixin, EntityView):
    __regid__ = 'apycot.te.description'
    __select__ = is_instance('TestExecution')

    changes_only = False

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<h2>%s</h2>' % xml_escape(entity.dc_title()))
        self.describe_execution(entity, changes_only=self.changes_only)


class TEChangeView(TEDescriptionView):
    __regid__ = 'apycot.te.changes'
    changes_only = True

class TEInContextView(baseviews.InContextView):
    __select__ = is_instance('TestExecution')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        status = '<span class="status_%s">%s</span>' % (
            entity.status, entity.printable_value('status'))
        if entity.starttime:
            status = self._cw._('%(date)s: %(status)s') % {
                'status': status,
                'date': entity.printable_value('starttime')}
        else:
            status = '[%s]' % status
        self.w('<a href="%s" title="%s">%s</a>' % (
               entity.absolute_url(),
               self._cw._('view details'),
               status))

class TEOutOfContextView(baseviews.OutOfContextView):
    __select__ = is_instance('TestExecution')

    def cell_call(self, row, col):
        self._cw.add_css('cubes.apycot.css')
        entity = self.cw_rset.get_entity(row, col)
        status = '<span class="status_%s">%s</span>' % (
            entity.status, entity.printable_value('status'))
        if entity.starttime:
            status = self._cw._('%(pe)s/%(config)s on %(date)s: %(status)s') % {
                'config': xml_escape(entity.configuration.dc_title()),
                'pe': xml_escape(entity.environment.dc_title()),
                'status': status,
                'date': entity.printable_value('starttime')}
        else:
            status = self._cw._('%(pe)s/%(config)s &lt;%(status)s&gt;') % {
                'config': xml_escape(entity.configuration.dc_title()),
                'pe': xml_escape(entity.environment.dc_title()),
                'status': status}
        self.w('<a href="%s" title="%s">%s</a>' % (
               entity.absolute_url(), self._cw._('view details'), status))


class TEDownloadBox(box.EntityBoxTemplate):
    __regid__ = 'apycot.te.download_box'
    __select__ = (box.EntityBoxTemplate.__select__ & is_instance('TestExecution') &
                  score_entity(lambda x: x.log_file))

    def cell_call(self, row, col, **kwargs):
        archive = self.cw_rset.get_entity(row, col).log_file[0]
        idownloadable.download_box(self.w, archive,
                                   self._cw._('download execution environment'))


class TEIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('TestExecution')

    def parent_entity(self):
        """hierarchy, used for breadcrumbs"""
        try:
            return self.entity.environment
        except IndexError: # XXX bw compat
            return self.entity.configuration

    def breadcrumbs(self, view=None, recurs=None):
        projectenv = self.parent_entity()
        breadcrumbs = projectenv.cw_adapt_to('IBreadCrumbs').breadcrumbs(view,
                                                                         recurs or set())
        if projectenv.__regid__ == 'ProjectEnvironment': # XXX bw compat
            breadcrumbs.append(self.entity.configuration)
        breadcrumbs.append(self.entity)
        return breadcrumbs


class TEIPrevNextAdapter(navigation.IPrevNextAdapter):
    __select__ = is_instance('TestExecution')

    def previous_entity(self):
        return self.entity.previous_execution()

    def next_entity(self):
        entity = self.entity
        rset = self._cw.execute(
            'Any X,TC ORDERBY X ASC LIMIT 1 '
            'WHERE X is TestExecution, X branch %(branch)s, X eid > %(x)s, '
            'X using_config TC, TC eid %(tc)s, '
            'X using_environment PE, PE eid %(pe)s',
            {'branch': entity.branch, 'x': entity.eid,
             'tc': entity.configuration.eid, 'pe': entity.environment.eid})
        if rset:
            return rset.get_entity(0, 0)


# CheckResult ##################################################################

_pvs.tag_attribute(('CheckResult', 'name'), 'hidden')
_pvs.tag_attribute(('CheckResult', 'status'), 'hidden')
_pvs.tag_attribute(('CheckResult', 'log'), 'relations')
_pvdc.tag_attribute(('CheckResult', 'log'), {'vid': 'narval.formated_log'})
_pvs.tag_subject_of(('CheckResult', 'during_execution', '*'), 'hidden')
_pvs.tag_object_of(('*', 'for_check', '*'), 'hidden')


class CRPrimaryView(TECheckResultsTab):
    __regid__ = 'primary'
    __select__ = is_instance('CheckResult')

    html_headers = no_robot_index

    def render_entity_title(self, entity):
        self._cw.add_css('cubes.apycot.css')
        self.w('<h4 id="%s" >%s [<span class="status_%s">%s</span>]</h4>'
               % (entity.anchored_name,
                  xml_escape(entity.name), entity.status, entity.status))



class CRStatusView(baseviews.InContextView):
    __select__ = is_instance('CheckResult')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w('<a href="%s" class="status_%s" title="%s">%s</a>' % (
               entity.absolute_url(),
               entity.status,
               self._cw._('view details'),
               self._cw._(entity.status)))


class CRIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('CheckResult')

    def parent_entity(self):
        return self.entity.execution


class CRIPrevNextAdapter(navigation.IPrevNextAdapter):
    __select__ = is_instance('CheckResult')

    def previous_entity(self):
        previous_exec = self.entity.execution.cw_adapt_to('IPrevNext').previous_entity()
        if previous_exec:
            return previous_exec.check_result_by_name(self.entity.name)

    def next_entity(self):
        next_exec = self.entity.execution.cw_adapt_to('IPrevNext').next_entity()
        if next_exec:
            return next_exec.check_result_by_name(self.entity.name)


class CRIIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('CheckResultInfo')

    def parent_entity(self):
        return self.entity.check_result

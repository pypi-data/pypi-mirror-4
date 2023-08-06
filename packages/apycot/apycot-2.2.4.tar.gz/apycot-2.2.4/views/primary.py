"""this module contains the primary views for apycot entities

:organization: Logilab
:copyright: 2008-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape
from logilab.common.tasksqueue import PRIORITY, MEDIUM

from cubicweb import Unauthorized, NoSelectableObject, tags
from cubicweb.selectors import (is_instance, has_related_entities, none_rset,
                                match_user_groups, match_kwargs, match_form_params,
                                score_entity)
from cubicweb.view import EntityView
from cubicweb.web import uicfg, box, formfields as ff, formwidgets as fwdgs
from cubicweb.web.views import tabs, forms, baseviews, tableview
from cubicweb.web.views import ibreadcrumbs

from cubes.narval.views import no_robot_index, startplan


_pvs = uicfg.primaryview_section
_pvdc = uicfg.primaryview_display_ctrl


class InheritedRelationView(EntityView):
    __regid__ = 'apycot.inherited'
    __select__ = match_kwargs('rtype')

    def cell_call(self, row, col, rtype, role):
        entity = self.cw_rset.get_entity(row, col)
        final = self._cw.vreg.schema.rschema(rtype).final
        owner, value = entity.owner_and_value(rtype, final)
        if owner is None:
            self.w(self._cw._('no value specified'))
        else:
            if final:
                self.w(owner.printable_value(rtype, value=value))
            else:
                self.w(value.view('incontext'))
            if owner is not entity:
                self.w(u' (%s)' % (self._cw._('inherited from %s')
                                   % owner.view('incontext')))


class InheritedConfigAttributeView(EntityView):
    __regid__ = 'apycot.inherited.config'
    __select__ = match_kwargs('rtype')

    def cell_call(self, row, col, rtype, role):
        prop = {'check_config': 'apycot_configuration',
                'check_environment': 'apycot_process_environment'}[rtype]
        entity = self.cw_rset.get_entity(row, col)
        parents = entity.config_parents()
        valdict = getattr(entity, prop)()
        owndict = getattr(entity, 'my_%s' % prop)
        values = []
        for key, val in valdict.items():
            if key in owndict:
                parent = ''
            else:
                for parent in parents:
                    gvaldict = getattr(parent, 'my_%s' % prop)
                    if key in gvaldict:
                        parent = parent.view('oneline')
                        break
                else:
                    parent = u'???' # XXX project env?
            if isinstance(val, list):
                for val in val:
                    values.append( (xml_escape(key), xml_escape(val), parent) )
            else:
                values.append( (xml_escape(key), xml_escape(val), parent) )
        if valdict:
            #self.w(u'<h4>%s</h4>' % label)
            headers = (self._cw._('key'), self._cw._('value'),
                       self._cw._('inherited from'))
            self.wview('pyvaltable', pyvalue=sorted(values), headers=headers)
        else:
            self.w(self._cw._('no value specified'))
            #self.field(label, self._cw._('no value specified'), tr=False)

_pvs.tag_attribute(('*', 'check_config'), 'attributes')
_pvdc.tag_attribute(('*', 'check_config'), {'vid': 'apycot.inherited.config'})
_pvs.tag_attribute(('*', 'check_environment'), 'attributes')
_pvdc.tag_attribute(('*', 'check_environment'), {'vid': 'apycot.inherited.config'})

# ProjectEnvironment ###########################################################

# custom view displaying repository, dealing with inheritance
_pvs.tag_subject_of(('ProjectEnvironment', 'local_repository', '*'), 'attributes')
_pvdc.tag_subject_of(('ProjectEnvironment', 'local_repository', '*'),
                     {'vid': 'apycot.inherited', 'rtypevid': True})
# custom view displaying all test configurations (including inherited config)
_pvs.tag_object_of(('*', 'use_environment', 'ProjectEnvironment'), 'relations')
_pvdc.tag_object_of(('*', 'use_environment', 'ProjectEnvironment'),
                    {'vid': 'apycot.pe.tc', 'rtypevid': True, 'showlabel': False})
# viewing reverse dependencies, should use outofcontext view defined below
_pvdc.tag_object_of(('*', 'on_environment', '*'),
                    {'subvid': 'outofcontext'})
# though dependencies are in the test configuration table, don't show them in
# automatic generation
_pvs.tag_object_of(('*', 'for_environment', '*'), 'hidden')
# in title
_pvs.tag_attribute(('ProjectEnvironment', 'name'), 'hidden')
# in breadcrumb
_pvs.tag_object_of(('*', 'has_apycot_environment', 'ProjectEnvironment'), 'hidden')
# in tab
_pvs.tag_object_of(('*', 'using_environment', 'ProjectEnvironment'), 'hidden')

class ProjectEnvironmentPrimaryView(tabs.TabbedPrimaryView):
    __select__ = is_instance('ProjectEnvironment')

    tabs = [_('apycot.pe.tab_config'), 'narval.recipe.tab_executions']
    default_tab = 'apycot.pe.tab_config'

    html_headers = no_robot_index


class PEConfigTab(tabs.PrimaryTab):
    __regid__ = 'apycot.pe.tab_config'
    __select__ = is_instance('ProjectEnvironment')


class PEExecutionTab(EntityView):
    # must be named like this for proper redirection to this tab when a test is started
    __regid__ = 'narval.recipe.tab_executions'
    __select__ = (is_instance('ProjectEnvironment') &
                  has_related_entities('using_environment', 'object'))

    html_headers = no_robot_index

    def entity_call(self, entity):
        project_rset = self._cw.execute('Any P WHERE P has_apycot_environment TC, TC eid %(e)s',
                                        {'e': entity.eid})
        self.wview('projectgraphtestresults', project_rset, 'null')
        rset = self._cw.execute(
            'Any T,TC,T,TB,TST,TET,TF, TS ORDERBY TST DESC WHERE '
            'T status TS, T using_config TC, T branch TB, '
            'T starttime TST, T endtime TET, T log_file TF?, '
            'T using_environment PE, PE eid %(pe)s',
            {'pe': entity.eid})
        self.wview('apycot.te.nopetable', rset, 'noresult')


class PETestConfigView(EntityView):
    __regid__ = 'apycot.pe.tc'
    __select__ = (is_instance('ProjectEnvironment')
                  & match_kwargs('rtype')
                  & score_entity(lambda x: x.all_configurations()))

    html_headers = no_robot_index

    def cell_call(self, row, col, rtype, role):
        assert rtype == 'use_environment' and role == 'object'
        self.w(u'<hr/>')
        pe = self.cw_rset.get_entity(row, col)
        if not pe.local_repository:
            self.w(u'<p class="warning">%s</p>' % self._cw._(
                u"Test configurations won't be startable until a repository is "
                "set on this environment"))
        self.w(u'<table class="projectEnvConfiguration">')
        self.w(u'<thead><tr><th>%s</th><th>%s</th><th>&#160;</th></tr></thead><tbody>'
               % (self._cw._('TestConfig'), self._cw._('TestDependency_plural')))
        for owner, tc in pe.all_configurations().values():
            self.w(u'<tr><td>')
            tc.view('oneline', w=self.w)
            if owner is not pe:
                self.w(u' (%s)' % self._cw._('inherited from %s') % owner.view('incontext'))
            self.w(u'</td><td>')
            rset = tc.environment_dependencies_rset(pe)
            if rset:
                self.wview('csv', rset)
            else:
                self.w(u'&#160;')
            self.w(u'</td><td>')
            if pe.local_repository:
                iwf = tc.cw_adapt_to('IWorkflowable')
                if iwf.state == 'activated':
                    try:
                        form = self._cw.vreg['forms'].select(
                            'apycot.starttestform', self._cw, entity=tc,
                            environment=pe)
                    except NoSelectableObject:
                        self.w(u'&#160;')
                    else:
                        form.render(w=self.w)
                else:
                    self.w(iwf.printable_state)
            self.w(u'</td></tr>')
        self.w(u'</tbody></table>')


class PEIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('ProjectEnvironment')
    def parent_entity(self):
        """hierarchy, used for breadcrumbs"""
        return self.entity.project


# TestConfig ##################################################

_pvdc.tag_attribute(('TestConfig', 'start_mode'),
                    {'vid': 'apycot.tc.startmode'})
_pvdc.tag_attribute(('TestConfig', 'start_rev_deps'),
                    {'vid': 'apycot.inherited'})
_pvs.tag_subject_of(('*', 'refinement_of', '*'), 'attributes')
_pvdc.tag_object_of(('*', 'refinement_of', '*'),
                    {'subvid': 'outofcontext'})
# custom view displaying repository, dealing with inheritance
_pvs.tag_subject_of(('TestConfig', 'use_recipe', '*'), 'attributes')
_pvdc.tag_subject_of(('TestConfig', 'use_recipe', '*'),
                     {'vid': 'apycot.inherited', 'rtypevid': True})
# in a tab
_pvs.tag_object_of(('*', 'using_config', 'TestConfig'), 'hidden')
# in title
_pvs.tag_attribute(('TestConfig', 'name'), 'hidden')
# handled py apycot.tc.startmode view
_pvs.tag_attribute(('TestConfig', 'computed_start_mode'), 'hidden')
#
_pvs.tag_object_of(('*', 'for_testconfig', 'TestConfig'), 'hidden')


class TCPrimaryView(tabs.TabbedPrimaryView):
    __select__ = is_instance('TestConfig')

    tabs = [_('apycot.tc.tab_config'), _('narval.recipe.tab_executions')]
    default_tab = 'apycot.tc.tab_config'

    html_headers = no_robot_index


class TCConfigTab(tabs.PrimaryTab):
    __select__ = is_instance('TestConfig')
    __regid__ = 'apycot.tc.tab_config'

    html_headers = no_robot_index


class TCExecutionTab(EntityView):
    __select__ = (is_instance('TestConfig') &
                  has_related_entities('using_config', 'object'))
    __regid__ = 'narval.recipe.tab_executions'

    html_headers = no_robot_index

    def entity_call(self, entity):
        rset = self._cw.execute(
            'Any T,PE,T,TB,TST,TET,TF, TS,PEN ORDERBY TST DESC WHERE '
            'T status TS, T using_config TC, T using_environment PE, '
            'T branch TB, T starttime TST, T endtime TET, T log_file TF?, '
            'PE name PEN, TC eid %(tc)s',
            {'tc': entity.eid})
        self.wview('apycot.te.notctable', rset, 'noresult')


class TCStartModeView(EntityView):
    __regid__ = 'apycot.tc.startmode'
    __select__ = is_instance('TestConfig') & match_kwargs('rtype')

    def cell_call(self, row, col, rtype, role):
        assert rtype == 'start_mode'
        tconfig = self.cw_rset.get_entity(row, col)
        self.w(tconfig.printable_value('computed_start_mode'))
        if tconfig.start_mode == 'inherited':
            self.w(self._cw._(' (inherited)'))


def _available_branches(form, field):
    tc = form.edited_entity
    environment = form.cw_extra_kwargs['environment']
    # if branch specified on the environment, don't let other choices
    envcfg = environment.apycot_configuration()
    if envcfg.get('branch'):
        return [envcfg['branch']]
    if environment.repository:
        return environment.repository.branches()
    return [tc.apycot_configuration().get('branch')]

def _default_branch(form, field):
    tc = form.edited_entity
    environment = form.cw_extra_kwargs['environment']
    cfg = tc.apycot_configuration(environment)
    if cfg.get('branch'):
        return cfg['branch']
    if environment.repository:
        return environment.repository.default_branch()
    return None

def _using_environment_value(form, field):
    return unicode(form.cw_extra_kwargs['environment'].eid)

def _startrevdeps_value(form, field):
    return form.edited_entity.start_reverse_dependencies and u'1' or u''

class TCStartForm(forms.EntityFieldsForm):
    __regid__ = 'apycot.starttestform'
    __select__ = (match_user_groups('managers', 'staff')
                  & match_kwargs('environment')
                  & is_instance('TestConfig')
                  & score_entity(lambda x: x.recipe and x.recipe.may_be_started()))

    form_renderer_id = 'htable'
    form_buttons = [fwdgs.SubmitButton(label=_('start test'))]
    @property
    def action(self):
        return self.edited_entity.absolute_url(base_url=self._cw.base_url(),
                                               vid='narval.startplan')

    using_environment = ff.StringField(widget=fwdgs.HiddenInput(),
                                       value=_using_environment_value)
    branch = ff.StringField(choices=_available_branches, label=_('vcs_branch'),
                            value=_default_branch)
    startrevdeps = ff.BooleanField(label=_('start_rev_deps'),
                                   value=_startrevdeps_value)
    archivetestdir = ff.BooleanField(label=_('archivetestdir'), value='')
    priority = ff.IntField(choices=[(label, str(val))
                                    for label, val in PRIORITY.items()],
                           value=str(MEDIUM),
                           label=_('execution priority'),
                           sort=False, internationalizable=True)


class StartTestView(startplan.StartPlanView):
    __select__ = (match_user_groups('managers', 'staff') & is_instance('TestConfig')
                  & match_form_params('using_environment')
                  & score_entity(lambda x: x.recipe and x.recipe.may_be_started()))

    def cell_call(self, row, col, priority=MEDIUM):
        testconfig = self.cw_rset.get_entity(row, col)
        # assigning to self.plan necessary since it's used by the parent class
        # to control redirection
        self.plan = testconfig.start(
            self._cw.entity_from_eid(self._cw.form['using_environment']),
            priority=int(priority), branch=self._cw.form.get('branch'),
            start_rev_deps=bool(self._cw.form.get('startrevdeps')),
            archive=bool(self._cw.form.get('archivetestdir')),
            check_duplicate=False)



# TestDependency ###############################################################

class TestDependencyOutOfContextView(baseviews.OutOfContextView):
    __select__ = is_instance('TestDependency')
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        entity.from_environment.view('oneline', w=self.w)
        self.w(u' ')
        entity.configuration.view('oneline', w=self.w)

class TestDependencyOneLineView(baseviews.OneLineView):
    __select__ = is_instance('TestDependency')
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(self._cw._('<a href="%s">dependency</a> for %s on %s)')
               % (entity.absolute_url(),
                  entity.configuration.view('oneline'),
                  entity.to_environment.view('oneline')))

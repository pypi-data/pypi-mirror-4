"""this module contains some stuff to integrate the apycot cube into jpl

:organization: Logilab
:copyright: 2009-2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.selectors import is_instance
from cubicweb.view import EntityView
from cubicweb.web import uicfg
from cubicweb.web.views import forms
from cubicweb.web.formfields import StringField, DateField
from cubicweb.web.views.formrenderers import EntityFormRenderer
from cubicweb.web import formwidgets as fwdgs, httpcache

_pvs = uicfg.primaryview_section
_pvs.tag_subject_of(('Project', 'has_apycot_environment', '*'), 'attributes')

# in graphs ignore branches that have less MIN_NB_RUNS_IN_GRAPH
MIN_NB_RUNS_IN_GRAPH = 3

def available_graphs(form, **attrs):
    entity = form.cw_rset.get_entity(0,0)
    testconfig_rset = form._cw.execute('Any TC,NAME WHERE P has_apycot_environment TENV, '
                                       'TC use_environment TENV, P eid %(p)s, TC name NAME',  {'p': entity.eid})
    branches_rset = form._cw.execute('Any B GROUPBY B WHERE TE branch B, '
                                     'TE is TestExecution, TE using_environment TENV, '
                                     'P has_apycot_environment TENV, P eid %(p)s HAVING COUNT(TE) > %(limit)s',
                                     {'p':entity.eid,
                                      'limit':MIN_NB_RUNS_IN_GRAPH})
    labels_and_values = []
    for branch in branches_rset:
        var_dict = {'p': entity.eid,
                    'branch':branch[0]}
        for testconfig in testconfig_rset:
            label = '%s : %s - %s' % (_(u'Test run time'), testconfig[1], branch[0])
            rql = 'Any TE,  ET - ST, S ORDERBY ST LIMIT 50 WHERE ' \
            'TE is TestExecution, TE using_environment TENV, ' \
            'P has_apycot_environment TENV, TE starttime ST, ' \
            'TE endtime ET, TE eid E, TE status S, P eid %(p)s, ' \
            'TE using_config TC, TC eid %(tc)s, TE branch "%(branch)s"'
            var_dict['tc'] = testconfig[0]
            rset = form._cw.execute(rql % var_dict)
            if rset and len(rset) > MIN_NB_RUNS_IN_GRAPH:
                js_call = form._cw.ajax_replace_url('graph-container',
                                                    rql= rql % var_dict,
                                                    vid='jqplot.testexecution')
                labels_and_values.append((label, js_call.replace('javascript: ', '')))

        for cri_label, label in (('pylint.evaluation', 'Pylint score'),
                                 ('cover-line-rate', 'Cover line rate')):
            label = '%s : %s' % (_(label), branch[0])
            rql = 'Any V ORDERBY D LIMIT 50 WHERE X is CheckResultInfo, X label "%(cri_label)s", ' \
                  'X value V, X for_check CR, CR during_execution TE, TE using_environment TENV, '\
                  'P has_apycot_environment TENV, P eid %(p)s, TE starttime D, TE branch "%(branch)s" '
            var_dict['cri_label'] = cri_label
            rset = form._cw.execute(rql % var_dict)
            if rset and len(rset) > MIN_NB_RUNS_IN_GRAPH:
                js_call = form._cw.ajax_replace_url('graph-container',
                                                    rql= rql % var_dict,
                                                    vid='jqplot.nonperiodic')
                labels_and_values.append((label, js_call.replace('javascript: ', '')))
    labels_and_values.reverse()
    return labels_and_values

class GraphRefreshForm(forms.FieldsForm):
    """Form to select what graph is being displayed"""
    __regid__ = 'select-graph'
    graphs = StringField(widget=fwdgs.Select(attrs={'onchange':'eval($("select#graphs").val())',
                                                    'onkeyup':'this.blur();this.focus();'}),
                         label=_('Graph:'),
                         choices=available_graphs)
    form_buttons = []
    form_renderer_id = 'nomaininfo'

class NoBoxEntityFormRenderer(EntityFormRenderer):
    __regid__ = 'nomaininfo'
    main_form_title = ''

class ProjectGraphTestResults(EntityView):
    """display project's graph from various execution results"""
    __regid__ = 'projectgraphtestresults'
    __select__ = is_instance('Project')

    def entity_call(self, entity):
        self.w(u'<h3>%s</h3>' % _('Time taken by Test Executions'))
        form = self._cw.vreg['forms'].select('select-graph', self._cw, rset=self.cw_rset)
        form.render(w=self.w)
        self._cw.add_onload('eval($("select#graphs").val())')
        self.w(u'<div id="graph-container"></div>')


class ProjectTestResultsTab(EntityView):
    """display project's test execution results"""
    __regid__ = title = _('apycottestresults_tab')
    __select__ = is_instance('Project')

    def entity_call(self, entity):
        self.wview('projectgraphtestresults', self.cw_rset, 'null')
        rset = self._cw.execute(
            'Any T,TC,T,TB,TST,TET,TF, TS ORDERBY TST DESC WHERE '
            'T status TS, T using_config TC, T branch TB, '
            'T starttime TST, T endtime TET, T log_file TF?, '
            'T using_environment PE, P has_apycot_environment PE, '
            'P eid %(p)s', {'p': entity.eid})
        self.wview('apycot.te.nopetable', rset, 'noresult')


# class VersionTestResultsVComponent(component.EntityVComponent):
#     """display the latest tests execution results"""
#     __regid__ = 'apycottestresults'
#     __select__ = component.EntityVComponent.__select__ & is_instance('Version')

#     context = 'navcontentbottom'
#     rtype = 'has_apycot_environment'
#     target = 'object'
#     title = _('Latest test results')
#     order = 11

#     def cell_call(self, row, col, **kwargs):
#         entity = self.cw_rset.get_entity(row, col)
#         configsrset = entity.related('has_apycot_environment')
#         if not configsrset:
#             return
#         self.wview('summary', configsrset, title=self._cw._(self.title))


def registration_callback(vreg):
    try:
        from cubes.tracker.views.project import ProjectPrimaryView
    except ImportError:
        pass
    else:
        has_jqplot = 'jqplot' in vreg.config.cubes()
        no_jqplot = [GraphRefreshForm, ProjectGraphTestResults]
        to_register = [value for value in globals().values() if has_jqplot or value not in no_jqplot]
        vreg.register_all(to_register, __name__)
        if 'apycottestresults_tab' not in ProjectPrimaryView.tabs:
            ProjectPrimaryView.tabs.append('apycottestresults_tab')

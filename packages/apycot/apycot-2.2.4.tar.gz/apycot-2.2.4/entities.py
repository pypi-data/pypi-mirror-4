"""this module contains the cube-specific entities' classes

:organization: Logilab
:copyright: 2008-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""

__docformat__ = "restructuredtext en"

from itertools import chain

from logilab.common.decorators import cached
from logilab.common.textutils import text_to_dict
from logilab.common.tasksqueue import LOW
from logilab.mtconverter import xml_escape

from cubicweb import ValidationError
from cubicweb.uilib import domid
from cubicweb.entity import _marker
from cubicweb.entities import AnyEntity, fetch_config

from cubes.narval.entities import Plan

def _anchor_name(data):
    """escapes XML/HTML forbidden characters in attributes and PCDATA"""
    return (data.replace('&', '').replace('<', '').replace('>','')
            .replace('"', '').replace("'", ''))


class ExecutionRSSMixin(object): # XXX move to an ui adapter

    RSS_LIMIT = 20

    def rss_label(self, vid='rss'):
        if vid == 'rss':
            return self._cw._(u'rss_exec_button')
        elif vid == 'changes_rss':
            return self._cw._(u'changes_rss_exec_button')
        else:
            assert False, 'unknow vid %s' % vid

    def rss_description(self, vid):
        raise NotImplementedError()

    def rss_rql(self, vid):
        raise NotImplementedError()


class RefinementMixIn(object):

    @property
    def config_parent(self):
        return self.refinement_of and self.refinement_of[0] or None

    def config_parents(self, _done=None):
        if _done is None:
            _done = set()
        _done.add(self.eid)
        result = [self]
        for parent in self.refinement_of:
            if parent.eid in _done:
                # XXX log error
                continue
            result += parent.config_parents(_done)
        return result

    def iter_refinements(self):
        yield self
        for refined in self.reverse_refinement_of:
            for refined in refined.iter_refinements():
                yield refined

    def _regroup_dict(self, prop):
        regroup = {}
        for parent in reversed(self.config_parents()):
            regroup.update(getattr(parent, prop))
        return regroup

    def owner_and_value(self, attr, isattr=False):
        for parent in self.config_parents():
            value = getattr(parent, attr)
            if isattr:
                if value is not None:
                    return parent, value
            elif value:
                return parent, value[0]
        return None, None

    def refined_attribute(self, attr):
        return self.owner_and_value(attr, True)[1]

    def refined_relation(self, attr):
        return self.owner_and_value(attr, False)[1]

    # apycot bot helpers #######################################################

    @property
    def my_apycot_configuration(self):
        return text_to_dict(self.check_config)

    def apycot_configuration(self):
        return self._regroup_dict('my_apycot_configuration')

    @property
    def my_apycot_process_environment(self):
        return text_to_dict(self.check_environment)

    def apycot_process_environment(self):
        return self._regroup_dict('my_apycot_process_environment')


# Project environment ##########################################################

class ProjectEnvironment(RefinementMixIn, ExecutionRSSMixin, AnyEntity):
    __regid__ = 'ProjectEnvironment'

    fetch_attrs, cw_fetch_order = fetch_config(['name', 'check_config', 'check_environment'])

    # rss related methods #####################################################

    # XXX move methods below to an adapter
    def rss_description(self, vid='rss'):
        data = {
            'pe': self.dc_title(),
            }
        if vid == 'rss':
            return self._cw._('Subscribe to all executions on %(pe)s') % data
        elif vid == 'changes_rss':
            return self._cw._('Subscribe to all changes of %(pe)s') % data
        else:
            assert False, 'unknow vid %s' % vid

    def rss_rql(self, vid='rss'):
        return 'TestExecution TE ORDERBY SD DESC LIMIT %i WHERE TE using_config TC, TE starttime SD, TC use_environment PE, PE eid %i'\
               % (self.RSS_LIMIT, self.eid)

    # cube specific logic #####################################################

    @property
    def project(self):
        """tracker integration"""
        if 'has_apycot_environment' in self._cw.vreg.schema:
            return self.refined_relation('reverse_has_apycot_environment')

    @property
    def repository(self):
        return self.refined_relation('local_repository')

    def dependencies(self, _done=None):
        if _done is None:
            _done = set()
        _done.add(self.eid)
        result = []
        if self.project:
            # XXX include recommends?
            for dp in chain(self.project.uses, self.project.recommends):
                # use getattr since for instance ExternalProject has no apycot
                # environment relation
                for dpe in getattr(dp, 'has_apycot_environment', ()):
                    if dpe.eid in _done:
                        continue
                    result.append(dpe)
                    result += dpe.dependencies(_done)
        return result

    # XXX no reverse dependencies without tracker
    def reverse_dependencies(self):
        result = []
        if self.project:
            for dp in chain(self.project.reverse_uses, self.project.reverse_recommends):
                for dpe in getattr(dp, 'has_apycot_environment', ()):
                    result.append(dpe)
        return result

    def all_configurations(self):
        cfgs = {}
        for parent in reversed(self.config_parents()):
            for tc in parent.reverse_use_environment:
                cfgs[tc.name] = (parent, tc)
        return cfgs

    def iter_configurations(self, startmode):
        for parent, tc in self.all_configurations().itervalues():
            if (tc.cw_adapt_to('IWorkflowable').state == 'activated'
                and tc.computed_start_mode == startmode):
                yield tc

    def configuration_by_name(self, name, checkstatus=True):
        for parent in reversed(self.config_parents()):
            for tc in parent.reverse_use_environment:
                if tc.name == name:
                    if not checkstatus or \
                           tc.cw_adapt_to('IWorkflowable').state == 'activated':
                        return tc
                    return


# Test configuration ###########################################################

class TestConfig(RefinementMixIn, ExecutionRSSMixin, AnyEntity):
    __regid__ = 'TestConfig'

    fetch_attrs, cw_fetch_order = fetch_config(['name', 'label', 'check_config',
                                             'check_environment'])

    def dc_title(self):
        return self.label or self.name

    # rss related methods #####################################################

    def rss_description(self, vid='rss'):
        data = {
            'conf': self.dc_title(),
            }
        if vid == 'rss':
            return self._cw._('Subscribe to all executions of %(conf)s') % data
        elif vid == 'changes_rss':
            return self._cw._('Subscribe to all changes of %(conf)s') % data
        else:
            assert False, 'unknow vid %s' % vid

    def rss_rql(self, vid='rss'):
        return 'TestExecution TE ORDERBY SD DESC LIMIT %i WHERE TE using_config TC, TE starttime SD, TC eid %i'\
               % (self.RSS_LIMIT, self.eid)

    # cube specific logic #####################################################

    @property
    def recipe(self):
        return self.refined_relation('use_recipe')

    @property
    def start_reverse_dependencies(self):
        return self.refined_attribute('start_rev_deps')

    def iter_environments(self):
        for penv in self.use_environment:
            yield penv
            for penv_ in penv.iter_refinements():
                if penv is penv_:
                    continue
                if penv_.configuration_by_name(self.name) is self:
                    yield penv_

    def apycot_configuration(self, environment=None):
        config = super(TestConfig, self).apycot_configuration()
        if environment is not None:
            config.update(environment.apycot_configuration())
        return config

    def environment_dependencies_rset(self, environment):
        return self._cw.execute(
            'Any DPE WHERE TC eid %(tc)s, X for_testconfig TC, '
            'PE eid %(pe)s, X for_environment PE, X on_environment DPE',
            {'tc': self.eid, 'pe': environment.eid})

    def dependencies(self, environment):
        _done = set()
        result = environment.dependencies(_done)
        for dpe in self.environment_dependencies_rset(environment).entities():
            if dpe.eid in _done:
                continue
            result.append(dpe)
            result += dpe.dependencies(_done)
        return result

    def match_branch(self, pe, branch):
        return self.apycot_configuration(pe).get('branch', branch) == branch

    def start(self, pe, branch=None, start_rev_deps=None, priority=LOW,
              archive=False, check_duplicate=True):
        if self.recipe is None:
            raise ValidationError(self.eid, {None: 'configuration has no recipe'})
        # don't overwrite branch hardcoded on the environment
        pecfg = pe.apycot_configuration()
        if pecfg.get('branch'):
            # make sure our configuration is consistent
            assert branch is None or branch == pecfg['branch']
            branch = pecfg['branch']
        elif branch is None: # XXX shouldn't occurs?
            branch = self.apycot_configuration().get('branch')
        if branch is None:
            branch = pe.repository.default_branch()
        cfg = self.apycot_configuration(pe)
        if cfg:
            arguments = u'Options(%s)' % cfg
        else:
            arguments = u'Options(%s)' % cfg
        duplicate_rset = check_duplicate and self._cw.execute(
            "Any X WHERE X branch %(branch)s, X status 'waiting execution', "
            "X using_environment PE, PE eid %(pe)s, "
            "X using_config TC, TC eid %(tc)s",
            {'branch': branch, 'pe': pe.eid, 'tc': self.eid})
        if duplicate_rset:
            assert len(duplicate_rset) == 1
            texec = duplicate_rset.get_entity(0,0)
            # if priority > duplicate.priority:
            #     duplicate.set_attributes(priority=priority)
            # if archive:
            #     for option_line in duplicate.options.splitlines():
            #         if option_line:
            #             option, value = option_line.split('=')
            #             if option == 'archive':
            #                 dup_arch = bool(value)
            #                 if not dup_arch:
            #                     duplicate.set_attributes(archive=False)
        else:
            options = u'archive=%s' % archive if archive else u''
            texec = self._cw.create_entity(
                'TestExecution', priority=priority, arguments=arguments,
                options=options, execution_of=self.recipe,
                branch=branch, using_environment=pe, using_config=self)
        if start_rev_deps or (start_rev_deps is None and self.start_reverse_dependencies):
            for dpe in pe.reverse_dependencies():
                tc = dpe.configuration_by_name(self.name)
                if tc is not None:
                    tc.start(dpe, branch=branch, start_rev_deps=False,
                             priority=priority)
        return texec


class TestExecution(Plan, ExecutionRSSMixin):
    __regid__ = 'TestExecution'

    def dc_title(self):
        if self.starttime:
            return self._cw._('%(date)s: %(status)s') % {
                'status': self.printable_value('status'),
                'date': self.printable_value('starttime')}
        else:
            return '<%(status)s>' % {
                'status': self.printable_value('status'),
                }

    def dc_long_title(self):
        if self.starttime:
            return self._cw._('%(pe)s/%(config)s on %(date)s: %(status)s') % {
                'status': self.printable_value('status'),
                'config': self.configuration.dc_title(),
                'pe': self.environment.dc_title(),
                'date': self.printable_value('starttime')}
        else:
            return self._cw._('%(pe)s/%(config)s <%(status)s>') % {
                'status': self.printable_value('status'),
                'config': self.configuration.dc_title(),
                'pe': self.environment.dc_title()}

    def dc_date(self, date_format=None):
        return self._cw.format_date(self.starttime, date_format=date_format)

    # rss related methods #####################################################

    def rss_description(self, vid='rss'):
        data = {
            'conf': self.configuration.dc_title(),
            'branch': self.branch,
            }
        if vid == 'rss':
            return self._cw._('Subscribe to all executions of %(conf)s for branch %(branch)s') % data
        elif vid == 'changes_rss':
            return self._cw._('Subscribe to all changes of %(conf)s for branch %(branch)s') % data
        else:
            assert False, 'unknow vid %s' % vid

    def rss_rql(self, vid='rss'):
        if self.branch is None:
            return 'TestExecution TE ORDERBY SD DESC LIMIT %i WHERE TE using_config TC, TC eid %i, TE branch NULL, TE starttime SD'\
                   % (self.RSS_LIMIT, self.configuration.eid)
        else:
            return 'TestExecution TE ORDERBY SD DESC LIMIT %i WHERE TE using_config TC, TC eid %i, TE branch "%s", TE starttime SD'\
                   % (self.RSS_LIMIT, self.configuration.eid, self.branch)

    # cube specific logic #####################################################

    @property
    def project(self):
        """tracker integration"""
        return self.environment.project

    @property
    def configuration(self):
        return self.using_config[0]

    @property
    def environment(self):
        return self.using_environment[0]

    @property
    def checkers(self):
        return self.reverse_during_execution

    def check_result_by_name(self, name):
        for cr in self.reverse_during_execution:
            if cr.name == name:
                return cr

    def previous_execution(self):
        rset = self._cw.execute(
            'Any X,TC ORDERBY X DESC LIMIT 1 '
            'WHERE X is TestExecution, X branch %(branch)s, X eid < %(x)s, '
            'X using_config TC, TC eid %(tc)s, '
            'X using_environment PE, PE eid %(pe)s',
            {'branch': self.branch, 'x': self.eid,
             'tc': self.configuration.eid, 'pe': self.environment.eid})
        if rset:
            return rset.get_entity(0, 0)

    @cached
    def status_changes(self):
        """return a dict containing status test changes between the previous
        execution and this one. Changes are described using a 2-uple:

          (previous status, current status)

        Return an empty dict if no previous execution is found or if nothing
        changed.
        """
        result = {}
        previous_exec = self.previous_execution()
        if previous_exec is None:
            return
        for cr in self.reverse_during_execution:
            previous_cr = previous_exec.check_result_by_name(cr.name)
            if previous_cr is not None and previous_cr.status != cr.status:
                result[cr.name] = (previous_cr, cr)
        return result

    def repository_revision(self, repository):
        for rev in self.using_revision:
            if rev.repository.eid == repository.eid:
                return rev


class CheckResult(AnyEntity):
    __regid__ = 'CheckResult'
    fetch_attrs, cw_fetch_order = fetch_config(['starttime', 'endtime',
                                             'name', 'status'])

    def absolute_url(self, *args, **kwargs):
        kwargs.setdefault('tab', domid(self.anchored_name))
        return self.execution.absolute_url(*args, **kwargs)

    @property
    def execution(self):
        return self.during_execution[0]

    @property
    def anchored_name(self):
        return _anchor_name(self.name)


class CheckResultInfo(AnyEntity):
    __regid__ = 'CheckResultInfo'
    fetch_attrs, cw_fetch_order = fetch_config(['type', 'label', 'value'])

    @property
    def check_result(self):
        return self.for_check[0]


class TestDependency(AnyEntity):
    __regid__ = 'TestDependency'

    @property
    def configuration(self):
        return self.for_testconfig[0]

    @property
    def from_environment(self):
        return self.for_environment[0]

    @property
    def to_environment(self):
        return self.on_environment[0]

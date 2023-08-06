"""apycot cube's specific schema

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from yams.buildobjs import (EntityType, RelationDefinition, SubjectRelation,
                            String, Datetime, Boolean)
from yams.reader import context

from cubicweb.schema import (RRQLExpression, RQLUniqueConstraint,
                             make_workflowable)

from cubes.narval.schema import IMMUTABLE_ATTR_PERMS, Plan

# tracker extension ############################################################

if 'Project' in context.defined:

    class has_apycot_environment(RelationDefinition):
        __permissions__ = {
            'read':   ('managers', 'users', 'guests'),
            'add':    ('managers', 'staff',
                       RRQLExpression('U has_update_permission S', 'S'),),
            'delete': ('managers', 'staff',
                       RRQLExpression('U has_update_permission S', 'S'),),
            }
        subject = 'Project'
        object = 'ProjectEnvironment'
        cardinality = '*?'
        composite = 'subject'

    CONF_WRITE_GROUPS = ('managers', 'staff')

else:

    CONF_WRITE_GROUPS = ('managers', )


# nosylist extension ###########################################################

if 'nosy_list' in context.defined:

    class interested_in(RelationDefinition):
        '''users to notify of changes concerning this entity'''
        subject = 'CWUser'
        object = 'ProjectEnvironment'

    class nosy_list(RelationDefinition):
        subject = ('ProjectEnvironment', 'TestExecution')
        object = 'CWUser'


# configuration entities and relations #########################################

def post_build_callback(schema):
    repoperms = schema['Repository'].permissions
    if not 'narval' in repoperms['read']:
        repoperms['read'] += ('narval',)
    for permission in ('add', 'update', 'delete'):
        for group in CONF_WRITE_GROUPS:
            if not group in repoperms[permission]:
                repoperms[permission] += (group,)
    for attr in ('path', 'local_cache'):
        rdef = schema['Repository'].rdef(attr)
        if not 'narval' in rdef.permissions['read']:
            rdef.permissions['read'] += ('narval',)
    # XXX has to be in post_build_callback since forge overwrite File
    # permissions
    if not 'narval' in schema['File'].permissions['add']:
        schema['File'].permissions['add'] += ('narval',)


class ProjectEnvironment(EntityType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests', 'narval'),
        'add':    CONF_WRITE_GROUPS,
        'update': CONF_WRITE_GROUPS,
        'delete': CONF_WRITE_GROUPS,
        }

    name = String(
        required=True, unique=True, maxsize=128,
        description=_('name for this environment')
        )
    check_config = String(
        description=_('preprocessor/checker options (one per line)'),
        fulltextindexed=True
        )
    check_environment = String(
        description=_('environment variables to be set in the check process '
                      'environment (one per line)'),
        fulltextindexed=True
        )
    # XXX used?
    vcs_path = String(
        description=_('relative path to the project into the repository')
        )


class TestConfig(EntityType):
    """apycot configuration to register a project branch to test"""
    __permissions__ = {
        'read':   ('managers', 'users', 'guests', 'narval'),
        'add':    CONF_WRITE_GROUPS,
        'update': CONF_WRITE_GROUPS,
        'delete': CONF_WRITE_GROUPS,
        }
    name = String(
        required=True, indexed=True, maxsize=128,
        description=_('name for this configuration'),
        constraints=[RQLUniqueConstraint('S name N, S use_environment E, '
                                         'Y use_environment E, Y name N', 'Y')]
        )
    label = String(
        unique=True, maxsize=128,
        description=_('label for this configuration (useful when name isn\'t unique)'),
        )

    start_mode = String(
        required=True,
        vocabulary=(_('inherited'), _('manual'), _('on new revision'),
                    _('hourly'), _('daily'),_('weekly'), _('monthly')),
        default='manual',
        description=_('when this test config should be started')
        )
    computed_start_mode = String(
        # when this test config should be started (automatically computed from
        # start_mode
        indexed=True,
        vocabulary=(_('manual'), _('on new revision'),
                    _('hourly'), _('daily'),_('weekly'), _('monthly')),
        default='manual',
        )
    start_rev_deps = Boolean(
        description=_("should tests for project environment depending on this "
                      "test's environment be started when this test is "
                      "automatically triggered")
        )
    check_config = String(
        description=_('preprocessor/checker options (one per line)'),
        fulltextindexed=True
        )
    check_environment = String(
        description=_('environment variables to be set in the test process '
                      'environment (one per line)'),
        fulltextindexed=True
        )
    # simply use 'branch=XXX'/'subpath=XXX' in check_config field. Get back
    # documentation before to remove code below
    #
    # vcs_branch  = String(
    #     description=_('branch to use for test\'s checkout. In case of '
    #                   'subversion repository, this should be the relative path '
    #                   'of the branch into the repository (vcs_path won\'t be '
    #                   'considered then).'),
    #     maxsize=256
    #     )
    # subpath = String(
    #     description=_('path relative to the checkout directory to be considered by tests')
    #     )

make_workflowable(TestConfig, in_state_descr=_('automatic test status'))


class TestDependency(EntityType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests', 'narval'),
        'add':    CONF_WRITE_GROUPS,
        'update': CONF_WRITE_GROUPS,
        'delete': CONF_WRITE_GROUPS,
        }
    for_environment = SubjectRelation('ProjectEnvironment', cardinality='1*',
                                      inlined=True, composite='object')
    for_testconfig = SubjectRelation('TestConfig', cardinality='1*',
                                     inlined=True, composite='object')
    on_environment = SubjectRelation('ProjectEnvironment', cardinality='1*',
                                     inlined=True, composite='object')


class use_environment(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests', 'narval'),
        'add':    CONF_WRITE_GROUPS,
        'delete': CONF_WRITE_GROUPS,
        }
    subject = 'TestConfig'
    object = 'ProjectEnvironment'
    cardinality = '**'
    composite = 'object'
    description=_('project environment in which this test config should be launched')
    constraints = [RQLUniqueConstraint('S name N, Y use_environment O, Y name N', 'Y')]


class use_recipe(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests', 'narval'),
        'add':    CONF_WRITE_GROUPS,
        'delete': CONF_WRITE_GROUPS,
        }
    subject = 'TestConfig'
    object = 'Recipe'
    cardinality = '?*'


class local_repository(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests', 'narval'),
        'add':    CONF_WRITE_GROUPS,
        'delete': CONF_WRITE_GROUPS,
        }
    subject = 'ProjectEnvironment'
    object = 'Repository'
    cardinality = '?*'
    description = _('vcsfile repository holding the source code')


# class needs_checkout(RelationDefinition):
#     __permissions__ = {
#         'read':   ('managers', 'users', 'guests', 'narval'),
#         'add':    CONF_WRITE_GROUPS,
#         'delete': CONF_WRITE_GROUPS,
#         }
#     subject = 'ProjectEnvironment'
#     object = 'ProjectEnvironment'
#     description = _('project\'s environments that should be installed from '
#                     'their repository to execute test for the environment or with this configuration')
#     #constraints=[RQLConstraint('NOT S identity O')]

class pe_refinement_of(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    CONF_WRITE_GROUPS,
        'delete': CONF_WRITE_GROUPS,
        }
    name = 'refinement_of'
    cardinality = '?*'
    subject = 'ProjectEnvironment'
    object = 'ProjectEnvironment'
    #constraints=[RQLConstraint('NOT S identity O')]

class tc_refinement_of(pe_refinement_of):
    subject = 'TestConfig'
    object = 'TestConfig'


# execution data entities and relations ########################################

BOT_ENTITY_PERMS = {
        'read':   ('managers', 'users', 'guests', 'narval'),
        'add':    ('narval',),
        'update': ('narval',),
        'delete': ('managers',),
        }
BOT_RELATION_PERMS = {
        'read':   ('managers', 'users', 'guests', 'narval'),
        'add':    ('narval',),
        'delete': ('managers',),
        }

class TestExecution(Plan):
    __specializes_schema__ = True
    __permissions__ = {
        'read':   ('managers', 'users', 'guests', 'narval'),
        'add':    CONF_WRITE_GROUPS,
        'update': ('narval',),
        'delete': CONF_WRITE_GROUPS,
        }
    # XXX overall_checks_status
    status = String(required=True, internationalizable=True, indexed=True,
                    default=u'waiting execution',
                    vocabulary=(_('waiting execution'), _('running'),
                                _('set up'), _('running tests'),
                                _('success'), _('partial'),
                                _('failure'), _('error'), _('nodata'),
                                _('missing'), _('skipped'),
                                _('killed'))
                    )
    branch = String(indexed=True, __permissions__=IMMUTABLE_ATTR_PERMS, required=True)
    log = String()


class CheckResult(EntityType):
    """group results of execution of a specific test on a project"""
    __permissions__ = BOT_ENTITY_PERMS

    name      = String(required=True, indexed=True, maxsize=128, description=_('check name'))
    status    = String(required=True,
                       vocabulary=(_('success'), _('partial'),
                                   _('failure'), _('error'), _('nodata'),
                                   _('missing'), _('skipped'),
                                   _('killed'), _('processing'))
                       )
    starttime = Datetime()
    endtime   = Datetime()
    log = String()


class CheckResultInfo(EntityType):
    """arbitrary information about execution of a specific test on a project"""
    __permissions__ = BOT_ENTITY_PERMS

    type = String(internationalizable=True, indexed=True)
    label = String(required=True, internationalizable=True)
    value = String(required=True, internationalizable=True)


class using_config(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests', 'narval'),
        'add':    CONF_WRITE_GROUPS,
        'delete': CONF_WRITE_GROUPS,
        }
    inlined = True
    subject = 'TestExecution'
    object = 'TestConfig'
    cardinality = '1*'
    composite = 'object'


class using_environment(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests', 'narval'),
        'add':    CONF_WRITE_GROUPS,
        'delete': CONF_WRITE_GROUPS,
        }
    inlined = True
    subject = 'TestExecution'
    object = 'ProjectEnvironment'
    cardinality = '1*'
    composite = 'object'


class during_execution(RelationDefinition):
    __permissions__ = BOT_RELATION_PERMS
    inlined = True
    subject = 'CheckResult'
    object = 'TestExecution'
    cardinality = '1*'
    composite = 'object'


class for_check(RelationDefinition):
    __permissions__ = BOT_RELATION_PERMS
    inlined = True
    subject = 'CheckResultInfo'
    object = ('CheckResult', 'TestExecution')
    cardinality = '1*'
    composite = 'object'


class using_revision(RelationDefinition):
    __permissions__ = BOT_RELATION_PERMS
    subject = 'TestExecution'
    object = 'Revision'
    description = _('link to revision which has been used in the test '
                    'environment for configurations which are linked to a '
                    'repository.')


class log_file(RelationDefinition):
    __permissions__ = BOT_RELATION_PERMS
    subject = 'TestExecution'
    object = 'File'
    cardinality = '??'
    composite = 'subject'

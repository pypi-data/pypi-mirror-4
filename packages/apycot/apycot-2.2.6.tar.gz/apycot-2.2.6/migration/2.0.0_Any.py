import os

add_relation_type('refinement_of') # other stuff will be implicitly added by add_cube side effect...

repo.system_source.dbhelper.set_null_allowed(
    session.pool['system'], 'cw_TestConfig', 'cw_start_mode', 'varchar(15)', True)
rename_entity_type('TestConfigGroup', 'TestConfig',
                   attrs=('name', 'check_config', 'check_environment', 'checks'))
rql('SET X refinement_of Y WHERE X use_group Y', ask_confirm=False) # XXX pb if use multiple groups
sql("UPDATE cw_TestConfig SET cw_start_mode='inherited' WHERE cw_start_mode IS NULL")
repo.system_source.dbhelper.set_null_allowed(
    session.pool['system'], 'cw_TestConfig', 'cw_start_mode', 'varchar(15)', False)


drop_relation_type('use_group')

add_cube('narval')


rql('SET X start_mode "manual" WHERE NOT X refinement_of Y, X start_mode "inherited"')
rql('SET X computed_start_mode SM WHERE X start_mode SM, NOT X start_mode "inherited"')

add_attribute('TestConfig', 'label') # except this one, dunno why

process_script(os.path.join(os.path.dirname(__file__), 'create_recipes.py'))

for tc in rqliter('Any X,XS,XC,XCC WHERE NOT X subpath NULL OR NOT X checks NULL, '
                  'X subpath XS, X checks XC, X check_config XCC').entities():
    config = tc.check_config or u''
    if tc.subpath:
        config += u'\nsubpath=%s' % tc.subpath
    if tc.checks:
        config += '\nXXXchecks=%s' % tc.checks
    tc.set_attributes(check_config=config)
drop_attribute('TestConfig' , 'subpath')
drop_attribute('TestConfig', 'checks')

for pe, tc, dpe in rqliter('Any PE,TC,DPE WHERE TC use_environment PE, TC needs_checkout DPE',
                           ask_confirm=True):
    rql('INSERT TestDependency X: X for_environment PE, X for_testconfig TC, X on_environment DPE'
        ' WHERE TC eid %(tc)s, PE eid %(pe)s, DPE eid %(dpe)s',
        {'tc': tc, 'pe': pe, 'dpe': dpe}, ask_confirm=False)
# PE needs_checkout PE when on PE's project dependency/recommend not needed,
# only backport TC needs_checkout PE if apycot as forge extension
if 'Project' not in schema:
    for pe, tc, dpe in rqliter('Any PE,TC,DPE WHERE TC use_environment PE, PE needs_checkout DPE',
                               ask_confirm=True):
        rql('INSERT TestDependency X: X for_environment PE, X for_testconfig TC, X on_environment DPE'
            ' WHERE TC eid %(tc)s, PE eid %(pe)s, DPE eid %(dpe)s',
            {'tc': tc, 'pe': pe, 'dpe': dpe}, ask_confirm=False)

drop_relation_type('needs_checkout')

for pe in rqliter('Any PE,PEPP,PEC WHERE PE is ProjectEnvironment,'
                  'PE check_preprocessors PEPP, PE check_config PEC',
                  ask_confirm=True).entities():
    if pe.check_preprocessors:
        if pe.check_config:
            cfg = u'%s\n%s' % (pe.check_config, pe.check_preprocessors)
        else:
            cfg = pe.check_preprocessors
        pe.set_attributes(check_config=cfg)

drop_attribute('ProjectEnvironment' , 'check_preprocessors')

rql('SET X execution_status "done" WHERE X is TestExecution')

# remove vcs_repository and vcs_repository_type (the local_repository
# relation is used instead) What's done:
# * only 'mercurial' and 'subversion' are automatically migrated (see
# vcsfile cube)
# * no change if 'local_repository' exists, use vcs_repository and
# vcs_repository_type otherwise.

repo_type_mapping = {'hg': u'mercurial',
                     'svn': u'subversion'}

for project in rqliter('Any P, R, T, L WHERE P is ProjectEnvironment, '
                       'P vcs_repository R, P vcs_repository_type T, P local_repository L?',
                       ask_confirm=False).entities():
    repo_type = repo_type_mapping.get(project.vcs_repository_type)
    if repo_type is None:
        print ('WARNING: "%s" repository type is no more managed, '
               'you have to manually upgrade %s.' % (project.vcs_repository_type,
                                                     project))
        continue
    if not project.local_repository and project.vcs_repository:
        reporset = rql('Repository X WHERE X path %(repo)s OR X source_url %(repo)s',
                       {'repo': project.vcs_repository}, ask_confirm=False)
        if reporset:
            project.set_relations(local_repository=reporset.get_entity(0, 0))
        elif project.vcs_repository.startswith('/'):
            rql('INSERT Repository R: R type %(type)s, R path %(path)s, '
                'P local_repository R WHERE P eid %(eid)s',
                {'type': repo_type, 'path': project.vcs_repository,
                 'eid': project.eid}, ask_confirm=True)
        else:
            rql('INSERT Repository R: R type %(type)s, R source_url %(path)s, '
                'P local_repository R WHERE P eid %(eid)s',
                {'type': repo_type, 'path': project.vcs_repository,
                 'eid': project.eid}, ask_confirm=True)
commit()

drop_attribute('ProjectEnvironment', 'vcs_repository')
drop_attribute('ProjectEnvironment', 'vcs_repository_type')

sync_schema_props_perms('TestExecution')
sync_schema_props_perms('TestConfig')
sync_schema_props_perms('use_environment')
sync_schema_props_perms('local_repository')
for ertype in ('CheckResult', 'CheckResultInfo', 'Repository'):
    sync_schema_props_perms(ertype, syncprops=False)

rql('DELETE TestExecution TE WHERE TE branch NULL')

# XXX encode to utf8 since sys.stdout.encoding is None
rset = rql('Any TC, N WHERE NOT TC use_recipe R, TC name N', ask_confirm=False)
if rset:
    print '*TestConfig* that do not have a *Recipe*:'
    print '\n'.join('  - %s (eid: %s)' % (entity.name.encode('utf8'), entity.eid)
                    for entity in rset.entities())


rset = rql('Any R WHERE R is Repository, R path NULL', ask_confirm=False)
if rset:
    print '*Repository* that do not have a *path*:'
    print '\n'.join('  - %s (eid: %s)' % (entity.dc_title().encode('utf8'), entity.eid)
                    for entity in rset.entities())

rset = rql('Any R WHERE R is Repository, R source_url NULL', ask_confirm=False)
if rset:
    print '*Repository* that do not have a *source_url*:'
    print '\n'.join('  - %s (eid: %s)' % (entity.dc_title().encode('utf8'), entity.eid)
                    for entity in rset.entities())

rset = rql('Any PE, N WHERE NOT PE local_repository LR, PE name N', ask_confirm=False)
if rset:
    print '*ProjectEnvironment* that do not have a *local_repository*:'
    print '\n'.join('  - %s (eid: %s)' % (entity.name.encode('utf8'), entity.eid)
                    for entity in rset.entities())

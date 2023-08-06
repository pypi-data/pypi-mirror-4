add_entity_type('ProjectEnvironment')
add_attribute('TestConfig', 'start_mode')
add_attribute('TestConfig', 'start_rev_deps')
add_attribute('TestConfig', 'subpath')
add_attribute('TestExecution', 'status')
sync_schema_props_perms(('TestConfig', 'name', 'String'))

# split existing TestConfig
if confirm('split existing test configs?'):
    pemap = {}
    for x in rql('TestConfig X WHERE NOT X vcs_repository_type "null"',
                 ask_confirm=False).entities():
        x.complete(attributes=False)
        regroup = {}
        for group in reversed(x.config_parts()):
            regroup.update(group.apycot_preprocessors)
        pps = u'\n'.join(u'%s=%s' % it for it in regroup.items())
        pe = create_entity('ProjectEnvironment', name=x.name,
                           vcs_repository_type=x.vcs_repository_type,
                           vcs_repository=x.vcs_repository,
                           vcs_path=x.vcs_path,
                           check_config=x.check_config,
                           check_environment=x.check_environment,
                           check_preprocessors=pps,
                           ask_confirm=False
                           )
        rql('SET Y local_repository R WHERE X local_repository R, X eid %(x)s, Y eid %(y)s',
            {'x': x.eid, 'y': pe.eid}, ('x', 'y'), ask_confirm=False)
        rql('SET X use_environment Y WHERE X eid %(x)s, Y eid %(y)s',
            {'x': x.eid, 'y': pe.eid}, ('x', 'y'), ask_confirm=False)
        pemap[x.vcs_repository] = pe.eid
    for x in rql('TestConfig X WHERE X vcs_repository_type "null"',
                 ask_confirm=False).entities():
        x.complete(attributes=False)
        pe = pemap[x.vcs_repository]
        assert not x.local_repository
        rql('SET X use_environment Y WHERE X eid %(x)s, Y eid %(y)s',
            {'x': x.eid, 'y': pe.eid}, ('x', 'y'), ask_confirm=False)

    for x in rql('TestConfig X WHERE NOT X quick_checks NULL',
                 ask_confirm=False).entities():
        x.complete(attributes=False)
        pe = pemap[x.vcs_repository]
        assert not x.local_repository
        newtc = create_entity('TestConfig', name=x.name + u' quick',
                              checks=x.quick_checks,
                              check_config=x.check_config,
                              check_environment=x.check_environment,
                              vcs_branch=x.vcs_branch,
                              ask_confirm=False
                              )
        rql('SET TC use_group G WHERE X use_group G, X eid %(x)s, TC eid %(tc)s',
            {'x': x.eid, 'tc': newtc.eid}, ('x', 'tc'), ask_confirm=False)
        rql('SET TC use_environment PE, PE start_as_dep_config TC '
            'WHERE X use_environment PE, X eid %(x)s, TC eid %(tc)s',
            {'x': x.eid, 'tc': newtc.eid}, ('x', 'tc'), ask_confirm=False)
        rql('SET TC needs_checkout PE WHERE X needs_checkout PE, X eid %(x)s, TC eid %(tc)s',
            {'x': x.eid, 'tc': newtc.eid}, ('x', 'tc'), ask_confirm=False)
    checkpoint()

    # fix needs_checkout relation
    rql('SET PE needs_checkout DPE '
        'WHERE TC use_environment PE, TC needs_checkout DTC, DTC use_environment DPE',
        ask_confirm=False)
    rql('SET TC needs_checkout DPE '
        'WHERE TC test_needs_checkout DTC, DTC use_environment DPE',
        ask_confirm=False)
    rql('SET TC needs_checkout DPE WHERE TC test_needs_checkout DTC, TDC use_environment DPE',
        ask_confirm=False)
    rql('DELETE TC needs_checkout DPE WHERE TC use_environment PE, PE needs_checkout DPE',
        ask_confirm=False)

for attr in ('vcs_repository_type', 'vcs_repository',
             'vcs_path', 'check_preprocessors',
             'quick_checks'):
    drop_attribute('TestConfigGroup', attr)
    drop_attribute('TestConfig', attr)

drop_attribute('TestConfigGroup', 'vcs_branch')
drop_relation_definition('TestConfigGroup', 'local_repository', 'Repository')
drop_relation_definition('TestConfig', 'local_repository', 'Repository')
drop_relation_definition('TestConfig', 'test_needs_checkout', 'TestConfig')
drop_relation_definition('TestConfig', 'needs_checkout', 'TestConfig')

if 'has_apycot_config' in schema:
    rql('SET P has_apycot_environment E WHERE P has_apycot_config TC, TC use_environment E')
    drop_relation_definition('Project', 'has_apycot_config', 'TestConfig')
    drop_relation_definition('Version', 'has_apycot_config', 'TestConfig')


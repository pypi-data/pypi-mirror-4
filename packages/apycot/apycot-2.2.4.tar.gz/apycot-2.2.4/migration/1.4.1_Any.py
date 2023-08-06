
if versions_map['apycot'][0] == (1, 4, 0):
    sync_schema_props_perms(('TestConfig', 'name', 'String'))
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
    drop_relation_definition('TestConfig', 'needs_checkout', 'TestConfig')
    drop_relation_definition('TestConfig', 'test_needs_checkout', 'TestConfig')
    drop_attribute('TestConfig', 'vcs_branch')
    drop_relation_definition('ProjectEnvironment', 'start_as_dep_config', 'TestConfig')

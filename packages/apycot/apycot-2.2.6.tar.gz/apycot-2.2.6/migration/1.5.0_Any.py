if 'nosylist' in config.cubes():
    add_relation_definition('CWUser', 'interested_in', 'ProjectEnvironment')
    add_relation_definition('CWUser', 'interested_in', 'TestConfig')
    add_relation_definition('TestConfig', 'nosy_list', 'CWUser')
    add_relation_definition('ProjectEnvironment', 'nosy_list', 'CWUser')
    add_relation_definition('TestExecution', 'nosy_list', 'CWUser')

sync_schema_props_perms(('TestConfig', 'name', 'String'))
sync_schema_props_perms('use_environment')

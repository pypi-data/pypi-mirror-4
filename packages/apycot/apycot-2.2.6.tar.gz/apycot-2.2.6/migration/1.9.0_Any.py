sync_schema_props_perms('TestExecution', syncperms=False)
sync_schema_props_perms('CheckResultInfo', syncperms=False)
sync_schema_props_perms('use_environment', syncprops=False)
sync_schema_props_perms('local_repository', syncprops=False)
if 'file' in config.cubes():
    add_relation_definition('TestExecution', 'log_file', 'File')
    sync_schema_props_perms('File', syncprops=False)
else:
    add_cube('file')

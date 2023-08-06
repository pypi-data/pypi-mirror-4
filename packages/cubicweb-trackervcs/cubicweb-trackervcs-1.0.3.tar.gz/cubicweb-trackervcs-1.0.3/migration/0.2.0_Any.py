for etype in ('Patch', 'Task', 'VersionContent', 'InsertionPoint'):
    if not (etype, 'CWPermission') in schema['require_permission'].rdefs:
        add_relation_definition(etype, 'require_permission', 'CWPermission')

sync_schema_props_perms('Patch', syncprops=False)
sync_schema_props_perms('Task', syncprops=False)

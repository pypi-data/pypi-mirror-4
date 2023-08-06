if 'patch_ticket' in schema:
    sync_schema_props_perms('patch_ticket')
drop_relation_definition('VersionContent', 'require_permission', 'CWPermission')

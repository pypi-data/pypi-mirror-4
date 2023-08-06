sync_schema_props_perms(syncprops=False)
if not ('require_permission' in schema and
        ('Repository', 'CWPermission') in schema['require_permission'].rdefs):
    add_relation_definition('Repository', 'require_permission', 'CWPermission')

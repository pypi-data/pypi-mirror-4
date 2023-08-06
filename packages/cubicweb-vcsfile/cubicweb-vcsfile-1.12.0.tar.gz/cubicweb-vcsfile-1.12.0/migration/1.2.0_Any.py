if 'ancestor_revision' not in fsschema:
    # some apps might want to keep it
    sql('DELETE FROM ancestor_revision_relation') # quick delete
    drop_relation_definition('Revision', 'ancestor_revision', 'Revision')

for rdef in ('Revision.description', 'Revision.author',
             'VersionedFile.directory', 'VersionedFile.name'):
    rdef = rdef.split('.')
    if len(rdef) < 3:
        rdef.append('String')
    sync_schema_props_perms(tuple(rdef), syncperms=False)

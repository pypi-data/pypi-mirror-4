Binary = repo.system_source._binary

for vceid, repoeid, dir, name, revnum in rql(
    'Any VC,REPO,D,N,R WHERE VC is VersionContent, '
    'VC from_revision REV, REV from_repository REPO, REV revision R, '
    'VC content_for VF, VF directory D, VF name N'):
    key = (str(repoeid), dir.encode('utf-8'), name.encode('utf-8'), str(revnum))
    key = '\x01'.join(key)
    sql('UPDATE cw_VersionContent as VC '
        'SET cw_data=%(data)s WHERE cw_eid=%(eid)s',
        {'data': Binary(key), 'eid': vceid}, ask_confirm=False)

sync_schema_props_perms('VersionContent', syncperms=False)

sql('DROP FUNCTION IF EXISTS version_data(bigint)')
sql('DROP FUNCTION IF EXISTS sys_path_init(text, text)')

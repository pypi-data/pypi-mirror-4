
dbdriver  = config.sources()['system']['db-driver']
if dbdriver == 'postgres':
    session.system_sql(
        "UPDATE cw_versioncontent "
        "SET cw_data = decode(t.cw_eid || e'\x01' || t.cw_directory || e'\x01' || t.cw_name || e'\x01' || t.cw_changeset, 'escape') "
        "FROM (SELECT cw_versioncontent.cw_data, cw_repository.cw_eid, cw_directory, cw_name, cw_revision, cw_changeset"
        "      FROM cw_repository, cw_revision, cw_versionedfile, cw_versioncontent"
        "      WHERE cw_revision.cw_from_repository = cw_repository.cw_eid"
        "        AND cw_versionedfile.cw_from_repository = cw_repository.cw_eid"
        "        AND cw_versioncontent.cw_content_for = cw_versionedfile.cw_eid"
        "        AND cw_versioncontent.cw_from_revision = cw_revision.cw_eid"
        "        AND cw_repository.cw_type = 'mercurial')"
        "     AS t "
        "WHERE t.cw_data = cw_versioncontent.cw_data")
    session.commit()
else:
    cu = session.system_sql(
        "SELECT cw_versioncontent.cw_eid, cw_versioncontent.cw_data, cw_revision.cw_changeset "
        " FROM cw_repository, cw_revision, cw_versionedfile, cw_versioncontent"
        " WHERE cw_revision.cw_from_repository = cw_repository.cw_eid"
        "   AND cw_versionedfile.cw_from_repository = cw_repository.cw_eid"
        "   AND cw_versioncontent.cw_content_for = cw_versionedfile.cw_eid"
        "   AND cw_versioncontent.cw_from_revision = cw_revision.cw_eid"
        "   AND cw_repository.cw_type = 'mercurial'")
    for row in cu:
        vceid = row[0]
        repoeid, directory, name, revnum = str(row[1]).split('\x01')
        data = '\x01'.join([repoeid, directory, name, row[2]])
        cur = session.cnxset.source_cnxs['system'][1].cursor()
        cur.execute('UPDATE cw_versioncontent SET cw_data = %(data)s WHERE cw_eid = %(eid)s',
                {'eid': vceid, 'data': data})
    session.commit()
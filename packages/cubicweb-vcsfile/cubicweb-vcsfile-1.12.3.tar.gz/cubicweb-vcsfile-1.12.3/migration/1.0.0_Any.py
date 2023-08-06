import os
from os.path import join, dirname
from cubicweb.server.sqlutils import sqlexec
from cubes.vcsfile.vcssource import get_vcs_source

vcssource = get_vcs_source(repo)

# dump the sqlite database
if confirm('backport sqlite database content?'):
    dumpfile = '/tmp/vcsfile.%s.sql' % config.appid
    dumpfile2 = '/tmp/vcsfile.%s.data.sql' % config.appid
    if os.system("sqlite3 %s .dump > %s" % (vcssource.dbpath, dumpfile)):
        import sys
        print 'error while dumping sqlite database'
        print 'is sqlite3 installed?'
        sys.exit(1)

    # filter out schema statement, import only 'data' statements (eg INSERT) into
    # the system database
    session.set_cnxset()
    cu = session.system_sql
    status = None # None | 'data' | 'schema'
    columns = []
    stmt = None

    def process_line(line, nextline):
        global cu, status, columns, stmt
        if status is None:
            stmttype = statement_type(line)
            if stmttype is None:
                #print 'skip', repr(line)
                return
            if stmttype == 'INSERT':
                status = 'data'
                assert columns
                # transform INSERT INTO "cw_Revision" into INSERT INTO cw_Revision
                # since the former is case sensitive while the later isn't
                insert, table, values = line.split('"', 2)
                # add columns name, they may be in different orders in the target
                # database
                line = '%s %s(%s) %s' % (insert, table, ','.join(columns), values)
            elif stmttype in ('CREATE', 'BEGIN', 'COMMIT'):
                columns = []
                status = 'schema'
        if status == 'data':
            if stmt is None:
                stmt = line
            else:
                stmt += line
        #else:
        #    print 'skip', repr(line)
        if status == 'schema':
            for w in line.split():
                w = w.replace('(', '').replace(')', '').strip()
                # islower to filter out table names
                if (w.startswith('cw_') or w.startswith('eid_')) and w.islower():
                    columns.append(w)
                if w == 'CONSTRAINT':
                    break
        if line.endswith(');\n'):
            # ensure next line is a new statement
            try:
                stmttype = statement_type(nextline)
            except:
                return
            if stmttype is None:
                return
            status = None
            if stmt:
                #print stmt
                cu(stmt)
            stmt = None

    def statement_type(line):
        try:
            stmttype, remaining = line.split(None, 1)
        except ValueError:
            #print 'skip', repr(line)
            return
        if stmttype in ('INSERT', 'CREATE', 'BEGIN', 'COMMIT'):
            return stmttype
        raise Exception('unknown statement type %s' % stmttype)

    prevline = None
    for line in file(dumpfile):
        if prevline is None:
            prevline = line
        else:
            process_line(prevline, line)
            prevline = line
    process_line(prevline, line)

    session.system_sql("UPDATE ENTITIES SET source='system' WHERE source='%s'"
                       % vcssource.uri)
    session.commit()

# now inline from_repository
sync_schema_props_perms('from_repository', syncperms=False)

session.set_cnxset()
fpath = join(dirname(__file__), '..', 'schema', '_regproc.sql.postgres')
sqlexec(file(fpath).read(), session.system_sql, withpb=False, delimiter=';;')
session.commit()

# remove vcssource from sources file
sources = config.read_sources_file()
del sources[vcssource.uri]
config.write_sources_file(sources)
# cleanup repo sources
del repo.sources[-1]
del repo.sources_by_uri[vcssource.uri]

# fix parent_revision relation of svn repo, broken in earlier version for
# revistion created through cw
for repoeid, in rql('Any R WHERE R is Repository, R type "subversion"',
                    ask_confirm=False):
    sql('INSERT INTO parent_revision_relation(eid_from, eid_to) '
        'SELECT R1.cw_eid, R2.cw_eid FROM cw_Revision as R1, cw_Revision as R2 '
        'WHERE NOT EXISTS(SELECT 1 FROM parent_revision_relation as p WHERE R1.cw_eid=p.eid_from AND R2.cw_eid=p.eid_to) '
        'AND R2.cw_revision = R1.cw_revision - 1 '
        'AND R1.cw_from_repository=%s AND R2.cw_from_repository=%s'
        % (repoeid, repoeid), ask_confirm=False)

from cubes.vcsfile.bridge import set_at_revision

rset = rql('Revision X ORDERBY R WHERE X revision R', ask_confirm=False)
for reid, in rset:
    set_at_revision(session, reid, safetybelt=True)

checkpoint()

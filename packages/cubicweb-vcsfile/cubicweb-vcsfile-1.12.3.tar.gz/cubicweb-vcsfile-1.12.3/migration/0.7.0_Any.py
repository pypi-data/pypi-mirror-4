add_attribute('Repository', 'type')
rql('SET X type "subversion" WHERE X is Repository')
add_entity_type('Revision')

drop_attribute('VersionContent', 'revision')
drop_attribute('VersionContent', 'description')
drop_attribute('VersionContent', 'author')
drop_attribute('DeletedVersionContent', 'revision')
drop_attribute('DeletedVersionContent', 'description')
drop_attribute('DeletedVersionContent', 'author')

from cubes.vcsfile.vcssource import get_vcs_source
import os

vcs_source = get_vcs_source(repo)
if os.path.exists(vcs_source.dbpath):
    print 'vcs source schema changed.'
    print 'the sqlite database %s has to be deleted.' % vcs_source.dbpath
    print 'repositories content will be reimported at the next startup.'
    if confirm('delete %s ?' % vcs_source.dbpath):
        os.remove(vcs_source.dbpath)
        # XXX now deactivate the vcs source ?
    else:
        print "delete this file manually else you'll run into trouble"

"""entity types used to represent a version control system (vcs) content

:organization: Logilab
:copyright: 2007-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from yams.buildobjs import (DEFAULT_ATTRPERMS,
                            EntityType, RelationDefinition,
                            String, Int, Boolean, Bytes)
from cubicweb.schema import RRQLExpression

PRIVATE_ATTRPERMS = DEFAULT_ATTRPERMS.copy()
PRIVATE_ATTRPERMS['read'] = ('managers',)
PRIVATE_ATTRPERMS['update'] = ('managers',)

RO_ATTRPERMS = DEFAULT_ATTRPERMS.copy()
RO_ATTRPERMS['update'] = ()
RO_RELPERMS = DEFAULT_ATTRPERMS.copy()
RO_RELPERMS['add'] = (RRQLExpression('X from_repository R, U in_group G, '
                                     'R require_permission P, P require_group G'))


class Repository(EntityType):
    """a local subversion repository which will be used as versionned content
    entity source
    """
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers',),
        'update': ('managers',),
        'delete': ('managers',),
        }

    title = String(description=_('optional title. If the repository has a public url, '
                                 'it may be a good idea to put it as title.'),
                   maxsize=256)
    type = String(required=True, vocabulary=('subversion', 'mercurial'),
                  description=_('repository\'s type'))
    source_url = String(description=_('source url (must be of the form protocol://path/to/stuff)'),
                        unique=True)
    path = String(unique=True,
                  description=_('absolute path to the local repository'),
                  __permissions__=PRIVATE_ATTRPERMS)
    local_cache = String(unique=True,
                         description=_('relative path to the local cache of the repository'),
                         __permissions__=PRIVATE_ATTRPERMS)
    subpath = String(description=_('if specified, only import the given subpart'
                                   ' of the repository (path relative to the '
                                   'repository root)'))
    encoding = String(default='utf-8', maxsize=20, required=True,
                      description=_('encoding used for the repository (e.g.'
                                    ' for file path and check-in comments)'))
    import_revision_content = Boolean(default=True,
                                      description=_('import contents of files touched by a revision. '
                                                    'It may cause performance issue when scaling.'))
    has_anonymous_access = Boolean(default=True,
                                   description=_('Tell if user needs an account to checkout the repository.'))


class Revision(EntityType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'users',),
        'update': ('managers', 'owners'),
        'delete': (),
        }
    __unique_together__ = [('from_repository', 'revision'),
                           # XXX behaviour vs NULL values depending on the
                           # backend? NULL values are not considered equals by
                           # sqlite nor postgres at least
                           ('from_repository', 'changeset')]
    # NOTE: creation_date will be set at revision date
    revision = Int(required=True, indexed=True,
                   description=_('revision number.'),
                   __permissions__=RO_ATTRPERMS)

    description = String(description=_('comment for this revision.'))

    author = String(indexed=True, maxsize=200,
                    description=_("author of this revision."))

    changeset = String(indexed=True, maxsize=100,
                       description=_('change set identifier, when used by the '
                                     'underlying version control system.'),
                   __permissions__=RO_ATTRPERMS)

    branch = String(indexed=True, maxsize=255,
                    description=_("branch of this revision."),
                   __permissions__=RO_ATTRPERMS)
    # XXX tags


class VersionedFile(EntityType):
    """a file stored in a versioned source"""
    __unique_together__ = [('from_repository', 'directory', 'name')]
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'users',),
        'update': (),
        'delete': (),
        }
    directory = String(required=True, indexed=True,
                       description=_('directory of the file in the repository.'),
                       __permissions__=RO_ATTRPERMS)
    name = String(required=True, fulltextindexed=True,
                  description=_('name of the file in the repository.'),
                   __permissions__=RO_ATTRPERMS)


class DeletedVersionContent(EntityType):
    """represent a revision where a versioned file has been deleted"""
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'users',),
        'update': ('managers', 'owners'),
        'delete': (),
        }


class VersionContent(DeletedVersionContent):
    """actual content of a versioned file, for a given revision"""
    data = Bytes(description=_("file's data"), required=True,
                 __permissions__=RO_ATTRPERMS)
    data_format = String(required=True, meta=True, maxsize=128,
                         description=_('MIME type of the file.'))
    data_encoding = String(meta=True, maxsize=32,
                           description=_('encoding of the file when it applies (e.g. text).'))


class from_repository(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (RRQLExpression('U in_group G, O require_permission P, '
                                  'P require_group G, P name "write"'),),
        'delete': (),
        }
    inlined = True
    subject = ('Revision', 'VersionedFile')
    object = 'Repository'
    cardinality = '1*'
    composite = 'object'

class content_for(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (RRQLExpression('O from_repository R, R require_permission P, '
                                  'U in_group G, P require_group G, P name "write"'),),
        'delete': (),
        }
    inlined = True
    subject = ('DeletedVersionContent', 'VersionContent')
    object = 'VersionedFile'
    composite = 'object'
    cardinality = '1*'

class from_revision(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (RRQLExpression('O from_repository R, R require_permission P, '
                                  'U in_group G, P require_group G, P name "write"'),),
        'delete': (),
        }
    inlined = True
    subject = ('DeletedVersionContent', 'VersionContent')
    object = 'Revision'
    cardinality = '1*'
    composite = 'object'

class parent_revision(RelationDefinition): # XXX ordered
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (RRQLExpression('O from_repository R, R require_permission P, '
                                  'U in_group G, P require_group G, P name "write"'),),
        'delete': (),
        }
    subject = 'Revision'
    object = 'Revision'

class at_revision(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (),
        'delete': (),
        }
    subject = ('DeletedVersionContent', 'VersionContent')
    object = 'Revision'

class vc_copy(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (RRQLExpression('O content_for VF, VF from_repository R, R require_permission P, '
                                  'U in_group G, P require_group G, P name "write"'),),
        'delete': (),
        }
    inlined = True
    subject = object = 'VersionContent'
    cardinality = '?*'

class vc_rename(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (RRQLExpression('O content_for VF, VF from_repository R, R require_permission P, '
                                  'U in_group G, P require_group G, P name "write"'),),
        'delete': (),
        }
    inlined = True
    subject = object = 'VersionContent'
    cardinality = '?*'


class granted_permission(RelationDefinition):
    subject = 'Repository'
    object = 'CWPermission'

class require_permission(RelationDefinition):
    subject = 'Repository'
    object = 'CWPermission'

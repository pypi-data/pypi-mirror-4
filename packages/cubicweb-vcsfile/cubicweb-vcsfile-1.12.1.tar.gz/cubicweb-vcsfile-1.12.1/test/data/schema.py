from yams.buildobjs import RelationDefinition
from yams.reader import context

if 'Tag' in context.defined:
    class tags(RelationDefinition):
        subject = 'Tag'
        object = 'VersionedFile'

if 'Folder' in context.defined:
    class filed_under(RelationDefinition):
        subject = 'VersionedFile'
        object = 'Folder'

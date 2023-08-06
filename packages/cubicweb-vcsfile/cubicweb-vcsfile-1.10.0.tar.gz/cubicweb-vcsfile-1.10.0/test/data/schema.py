from yams.buildobjs import RelationDefinition

class tags(RelationDefinition):
    subject = 'Tag'
    object = 'VersionedFile'

class filed_under(RelationDefinition):
    subject = 'VersionedFile'
    object = 'Folder'        

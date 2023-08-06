"""cubicweb-vcsfile"""

IMMUTABLE_ATTRIBUTES = frozenset(('VersionedFile.directory',
                                  'VersionedFile.name',
                                  'VersionedFile.from_repository',
                                  'Revision.revision',
                                  'Revision.changeset',
                                  'Revision.branch',
                                  'Revision.from_repository',
                                  'DeletedVersionContent.from_revision',
                                  'DeletedVersionContent.content_for',
                                  'VersionContent.from_revision',
                                  'VersionContent.content_for',
                                  'VersionContent.data',
                                  ))

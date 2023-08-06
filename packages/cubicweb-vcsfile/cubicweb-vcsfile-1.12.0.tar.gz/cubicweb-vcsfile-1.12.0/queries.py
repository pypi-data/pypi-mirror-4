def new_revision_rql(has_parent, has_precursor=False, set_all=False):
    """return rql to insert a revision entity

    substitutions used:
    * description, author, branch, repoeid (mandatory)
    * parent (if `has_parent` is True)
    * date, revision, changeset (if `set_all` is True)
    """
    rql = ('INSERT Revision R: R description %(description)s, '
           'R author %(author)s, R branch %(branch)s, R from_repository X, '
           'R phase %(phase)s, R hidden %(hidden)s')
    if set_all:
        rql += ', R revision %(revision)s, R changeset %(changeset)s'
        rql += ', R creation_date %(date)s' # XXX use specific field
    if has_parent:
        rql += ', R parent_revision PR'
    if has_precursor:
        rql += ', R obsoletes PREC'
    rql += ' WHERE X eid %(repoeid)s'
    if has_parent:
        rql += ', PR eid %(parent)s'
    if has_precursor:
        rql += ', PREC eid %(precursor)s'
    return rql

def new_file_rql():
    return ('INSERT VersionedFile X: X from_repository R, '
            'X directory %(directory)s, X name %(name)s WHERE R eid %(repoeid)s')

def new_file_content_rql():
    return ('INSERT VersionContent X: X content_for VF, X from_revision REV, '
            'X data %(data)s WHERE VF eid %(vfeid)s, REV eid %(reveid)s')

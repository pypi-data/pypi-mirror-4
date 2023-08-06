
add_attribute('Revision', 'phase')
rql('SET R phase "public" WHERE R is Revision')

add_relation_type('obsoletes')

add_attribute('Revision', 'hidden')
rql('SET R hidden False WHERE R is Revision')

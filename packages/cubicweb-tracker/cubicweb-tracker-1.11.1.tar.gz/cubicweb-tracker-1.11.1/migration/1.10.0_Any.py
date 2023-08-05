add_cube('iprogress')
add_cube('localperms')
add_relation_definition('Project', 'granted_permission', 'CWPermission')
rql('SET X granted_permission P WHERE X require_permission P, X is Project')

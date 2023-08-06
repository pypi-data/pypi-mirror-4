add_attribute('Repository', 'use_global_groups')
sync_schema_props_perms('patch_name')
add_relation_definition('Comment', 'comments', 'Task')

rql('''
INSERT Task T:
    T title "placeholder Task",
    T description "house free comment after 1.1.0 migration",
    P has_activity T,
    C comments T
WHERE
    C comments P,
    P is Patch''')
drop_relation_definition('Comment', 'comments', 'Patch')

rql('''
INSERT Task T:
    T title "placeholder Task",
    T description "house free comment after 1.1.0 migration",
    IP has_activity T,
    C comments T
WHERE
    C comments IP,
    IP is InsertionPoint''')
drop_relation_definition('Comment', 'comments', 'InsertionPoint')
commit()

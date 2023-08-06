# update workflow condition

add_attribute('Repository', 'has_review')
rql('SET R has_review False', ask_confirm=True)
commit()


rql('Set R repository_committer U '
    'WHERE R has_patch_repository PR, PR repository_committer U',
    ask_confirm=True)
rql('Set R repository_reviewer U '
    'WHERE R has_patch_repository PR, PR repository_reviewer U',
    ask_confirm=True)

rql('Set R has_review True WHERE R has_patch_repository PR', ask_confirm=True)
commit()
rql('DELETE Repository PR WHERE R has_patch_repository PR', ask_confirm=True)
commit()

drop_relation_type('has_patch_repository')

drop_attribute('Patch', 'branch')
drop_attribute('Patch', 'originator')

drop_relation_type('patch_repository')

add_relation_definition('Patch', 'patch_revision', 'Revision')
drop_relation_definition('Patch', 'patch_revision', 'VersionContent')
drop_relation_definition('Patch', 'patch_revision', 'DeletedVersionContent')

drop_relation_type('applied_at')

drop_relation_type('patch_depends_on')


add_relation_definition('InsertionPoint', 'point_of', 'Revision')
drop_relation_definition('InsertionPoint', 'point_of', 'VersionContent')

add_relation_definition('Revision', 'nosy_list', 'CWUser')
drop_relation_definition('VersionContent', 'nosy_list', 'CWUser')
drop_relation_definition('DeletedVersionContent', 'nosy_list', 'CWUser')

rql('DELETE Patch P', ask_confirm=True)
commit()

# all patches are gone, so no need to keep and update the old wf
wf = get_workflow_for('Patch')
wf.cw_delete()
commit()
from cubes.vcreview.workflows import define_patch_workflow
define_patch_workflow(add_workflow)
commit()

sync_schema_props_perms()

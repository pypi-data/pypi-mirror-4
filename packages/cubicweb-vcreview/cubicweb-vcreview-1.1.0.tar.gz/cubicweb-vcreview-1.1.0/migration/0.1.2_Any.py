sync_schema_props_perms('Patch', syncprops=False)
sync_schema_props_perms('patch_repository', syncprops=False)
sync_schema_props_perms('patch_revision', syncprops=False)
sync_schema_props_perms('applied_at', syncprops=False)


pwf = rql('Workflow X WHERE X name "patch workflow"').get_entity(0, 0)
folded  = pwf.add_state(_('folded'))
inprogress = pwf.state_by_name('in-progress')
pending = pwf.state_by_name('pending-review')
deleted = pwf.state_by_name('deleted')
pwf.add_transition(_('fold'), (inprogress, pending, deleted), folded,
                   ('managers',),)


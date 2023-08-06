pwf = rql('Workflow X WHERE X name "patch workflow"').get_entity(0, 0)
inprogress = pwf.state_by_name('in-progress')
deleted = pwf.state_by_name('deleted')
pwf.add_transition(_('reopen'), deleted, inprogress,
                   ('managers',))


add_attribute('Patch', 'branch')
add_attribute('Patch', 'originator')

for patch in rql('Patch X').entities():
    revision = patch.revisions[0].rev
    patch.set_attributes(branch=revision.branch, originator=revision.author)


add_relation_definition('CWUser', 'interested_in', 'Patch')
add_relation_definition('VersionContent', 'nosy_list', 'CWUser')
add_relation_definition('DeletedVersionContent', 'nosy_list', 'CWUser')
add_relation_definition('InsertionPoint', 'nosy_list', 'CWUser')

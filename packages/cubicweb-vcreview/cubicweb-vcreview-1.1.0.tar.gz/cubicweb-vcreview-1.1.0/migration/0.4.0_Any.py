create_entity('CWGroup', name=u'reviewers')
create_entity('CWGroup', name=u'committers')
add_relation_type('repository_committer')
add_relation_type('repository_reviewer')
add_relation_type('patch_reviewer')
add_relation_type('patch_depends_on')


pwf = get_workflow_for('Patch', ask_confirm=False)
inprogress = pwf.state_by_name('in-progress')
pending    = pwf.state_by_name('pending-review')
applied    = pwf.state_by_name('applied')
rejected   = pwf.state_by_name('rejected')
folded     = pwf.state_by_name('folded')
deleted    = pwf.state_by_name('deleted')

reviewed   = pwf.add_state('reviewed')
pwf.add_transition(_('apply'), (inprogress, pending, deleted), applied,
                   ('managers',))

accept = pwf.transition_by_name('accept')
accept.set_relations(destination_state=reviewed)
reviewed.set_relations(allowed_transition=[pwf.transition_by_name('refuse'),
                                           pwf.transition_by_name('fold'),
                                           pwf.transition_by_name('apply'),
                                           pwf.transition_by_name('reject')])
for trname in ('accept', 'refuse', 'fold'):
    pwf.transition_by_name(trname).set_permissions(
        ('reviewers',),
        'X patch_repository R, R repository_reviewer U',
        reset=False)

for transition in pwf.reverse_transition_of:
    transition.set_permissions(
        ('committers',), 'X patch_repository R, R repository_committer U',
        reset=False)

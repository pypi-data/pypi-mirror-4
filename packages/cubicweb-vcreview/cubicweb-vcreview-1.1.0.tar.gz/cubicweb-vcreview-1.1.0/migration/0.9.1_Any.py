pwf = get_workflow_for('Patch', ask_confirm=False)
reviewed = pwf.state_by_name('reviewed')
ask = pwf.transition_by_name('ask review')
rql('SET S allowed_transition T WHERE S eid %(s)s, T eid %(t)s, NOT S allowed_transition T',
    {'s': reviewed.eid, 't': ask.eid})

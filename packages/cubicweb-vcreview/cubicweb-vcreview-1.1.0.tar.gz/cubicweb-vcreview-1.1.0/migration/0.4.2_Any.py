pwf = get_workflow_for('Patch', ask_confirm=False)
delete = pwf.transition_by_name('file deleted')
reviewed = pwf.state_by_name('reviewed')
rql('SET S allowed_transition T WHERE S eid %(s)s, T eid %(t)s, NOT S allowed_transition T',
    {'s': reviewed.eid, 't': delete.eid})

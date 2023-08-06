pwf = get_workflow_for('Patch', ask_confirm=False)
deleted = pwf.state_by_name('deleted')
accept = pwf.transition_by_name('accept')
rql('DELETE S allowed_transition T WHERE S eid %(s)s, T eid %(t)s',
    {'s': deleted.eid, 't': accept.eid})

refuse = pwf.transition_by_name('refuse')
refuse.set_attributes(name=u'ask rework')

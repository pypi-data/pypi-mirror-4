wf = get_workflow_for('Task')
for name in ('done', 'start'):
    tr = wf.transition_by_name(name)
    for cond in tr.condition:
        expr = cond.expression.replace('P patch_repository R', 'P patch_revision RE, RE from_repository R')
        expr = expr.replace('IP point_of VC, P patch_revision VC', 'IP point_of RE, P patch_revision RE')
        if expr != cond.expression:
            cond.set_attributes(expression=expr)

commit()

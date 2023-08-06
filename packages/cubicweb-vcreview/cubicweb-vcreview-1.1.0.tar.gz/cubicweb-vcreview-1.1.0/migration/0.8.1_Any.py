conditions = [
    # global reviewer / committer
    'Z has_activity X, U in_group G, G name IN ("reviewers", "committers")',
    # repository reviewer / committer
    'P has_activity X, P patch_repository R, EXISTS(R repository_reviewer U) OR EXISTS(R repository_committer U)',
    'IP has_activity X, IP point_of VC, P patch_revision VC, P patch_repository R, EXISTS(R repository_reviewer U) OR EXISTS(R repository_committer U)',
    # patch owner
    'P has_activity X, P owned_by U',
    'IP has_activity X, IP point_of VC, P patch_revision VC, P owned_by U',
    ]
task_wf = get_workflow_for('Task')
task_wf.transition_by_name('start').set_permissions(conditions=conditions, reset=False)
task_wf.transition_by_name('done').set_permissions(conditions=conditions, reset=False)

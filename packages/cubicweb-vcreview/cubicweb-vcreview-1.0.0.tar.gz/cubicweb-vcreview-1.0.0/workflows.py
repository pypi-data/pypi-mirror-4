
def define_patch_workflow(add_workflow):
    pwf = add_workflow(_('patch workflow'), 'Patch')

    inprogress = pwf.add_state(_('in-progress'), initial=True)
    pending    = pwf.add_state(_('pending-review'))
    reviewed   = pwf.add_state(_('reviewed'))
    applied    = pwf.add_state(_('applied'))
    rejected   = pwf.add_state(_('rejected'))
    folded     = pwf.add_state(_('folded'))
    outdated   = pwf.add_state(_('outdated'))

    pwf.add_transition(_('ask review'), (inprogress, reviewed, outdated), pending,
                       ('managers', 'users',)) # XXX patch owner only?
    pwf.add_transition(_('accept'), (inprogress, pending), reviewed,
                       ('managers', 'committers', 'reviewers',),
                       ('X patch_revision RE, RE from_repository R, R repository_committer U',
                        'X patch_revision RE, RE from_repository R, R repository_reviewer U')) # XXX patch_reviewer/repo manager only?
    pwf.add_transition(_('ask rework'), (pending, reviewed), inprogress,
                       ('managers', 'committers', 'reviewers',),
                       ('X patch_revision RE, RE from_repository R, R repository_committer U',
                        'X patch_revision RE, RE from_repository R, R repository_reviewer U')) # XXX patch_reviewer/repo manager only? ignore patch_reviewer if in reviewed state?
    pwf.add_transition(_('fold'), (inprogress, pending, outdated, reviewed), folded,
                       ('managers', 'committers', 'reviewers',),
                       ('X patch_revision RE, RE from_repository R, R repository_committer U',
                        'X patch_revision RE, RE from_repository R, R repository_reviewer U')) # XXX patch owner/repo mananger only?
    pwf.add_transition(_('apply'), (inprogress, pending, outdated, reviewed), applied,
                       ('managers', 'committers',),
                       'X patch_revision RE, RE from_repository R, R repository_committer U')
    pwf.add_transition(_('reject'), (inprogress, pending, outdated, reviewed), rejected,
                       ('managers', 'committers',),
                       'X patch_revision RE, RE from_repository R, R repository_committer U')
    # internal transition, not available through the ui
    # XXX we've to put 'managers' group since transition without groups
    # nor condition are fireable by anyone...
    pwf.add_transition(_('obsolete'), (inprogress, pending, reviewed), outdated,
                       ('managers',))
    # in case hooks following patch state made a mistake, we should be able to
    # reopen the patch
    pwf.add_transition(_('reopen'), outdated, inprogress,
                       ('managers', 'committers',),
                       'X patch_revision RE, RE from_repository R, R repository_committer U')

# copyright 2011-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-vcreview postcreate script, executed at instance creation time or when
the cube is added to an existing instance.

You could setup site properties or a workflow here for example.
"""

from cubes.vcreview.workflows import define_patch_workflow

define_patch_workflow(add_workflow)

commit()

# change task workflow permission
conditions = [
    # global reviewer / committer
    'Z has_activity X, U in_group G, G name IN ("reviewers", "committers")',
    # repository reviewer / committer
    'P has_activity X, P patch_revision RE, RE from_repository R, EXISTS(R repository_reviewer U) OR EXISTS(R repository_committer U)',
    'IP has_activity X, IP point_of RE, P patch_revision RE, RE from_repository R, EXISTS(R repository_reviewer U) OR EXISTS(R repository_committer U)',
    # patch owner
    'P has_activity X, P owned_by U',
    'IP has_activity X, IP point_of RE, P patch_revision RE, P owned_by U',
    ]
task_wf = get_workflow_for('Task')
task_wf.transition_by_name('start').set_permissions(conditions=conditions, reset=False)
task_wf.transition_by_name('done').set_permissions(conditions=conditions, reset=False)

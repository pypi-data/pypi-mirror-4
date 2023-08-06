# copyright 2011-2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-vcreview schema"""

__docformat__ = "restructuredtext en"
_ = unicode

from yams.buildobjs import EntityType, RelationDefinition, String, Int

from cubicweb.schema import WorkflowableEntityType, RQLConstraint, RRQLExpression

# XXX nosylist. notifications: send all review (eg task + commment) at wf transition time


class has_patch_repository(RelationDefinition):
    """the patch repository will have patch entities generated for file stored
    in it.
    """
    subject = 'Repository'
    object = 'Repository'
    cardinality = '*?'


# the patch entity #############################################################

class Patch(WorkflowableEntityType):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': (), # created by an internal session in a looping task
        'update': ('managers', 'users'),
        'delete': ('managers',),
        }
    branch = String(
        maxsize=100, indexed=True,
        description=_('branch where this patch has been introduced'))
    originator = String(
        maxsize=256, indexed=True,
        description=_('author of the revision which has introduced this patch'))
    patch_name = String(
        required=True,
        description=_('name of the patch in the repository'))


class patch_repository(RelationDefinition):
    # shortcut for P patch_revision VC, VC revision REV, REV from_repository R
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': (), # created by an internal session in a looping task
        'delete': (),
        }
    subject = 'Patch'
    object = 'Repository'
    cardinality = '1*'
    composite = 'object'
    inlined = True

class patch_revision(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': (), # created by an internal session in a looping task
        'delete': (),
        }
    subject = 'Patch'
    object = ('VersionContent', 'DeletedVersionContent')
    cardinality = '+*'

class applied_at(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers',),
        'delete': ('managers',),
        }
    subject = 'Patch'
    object = 'Revision'
    cardinality = '??'
    constraints = [RQLConstraint('S patch_repository PR, O from_repository R, '
                                 'R has_patch_repository PR')]

class repository_committer(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers',),
        'delete': ('managers',),
        }
    subject = 'Repository'
    object = 'CWUser'

class repository_reviewer(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'committers',
                RRQLExpression('S has_patch_repository R, R repository_committer U')),
        'delete': ('managers', 'committers',
                   RRQLExpression('S has_patch_repository R, R repository_committer U')),
        }
    subject = 'Repository'
    object = 'CWUser'

class patch_reviewer(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'committers',
                RRQLExpression('S patch_repository R, R repository_committer U')),
        'delete': ('managers', 'committers',
                   RRQLExpression('S patch_repository R, R repository_committer U')),
        }
    subject = 'Patch'
    object = 'CWUser'
    constraints = [RQLConstraint('EXISTS(O in_group G, G name "reviewers") '
                                 'OR EXISTS(S patch_repository R, R repository_reviewer O)')]

class patch_committer(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'committers',
                RRQLExpression('S patch_repository R, R repository_committer U')),
        'delete': ('managers', 'committers',
                   RRQLExpression('S patch_repository R, R repository_committer U')),
        }
    subject = 'Patch'
    object = 'CWUser'
    constraints = [RQLConstraint('EXISTS(O in_group G, G name "committers") '
                                 'OR EXISTS(S patch_repository R, R repository_committer O)')]

class patch_depends_on(RelationDefinition):
    subject = 'Patch'
    object = 'Patch'

# ability to reference diff chunks #############################################

class InsertionPoint(EntityType):
    __unique_together__ = [('lid', 'point_of')]
    lid = Int(indexed=True, required=True)

class point_of(RelationDefinition):
    subject = 'InsertionPoint'
    object = 'VersionContent'
    cardinality = '1*'
    composite = 'object'
    inlined = True


# activities ###################################################################

class has_activity(RelationDefinition):
    subject = ('Patch', 'InsertionPoint')
    object = 'Task'
    cardinality = '*?'
    composite = 'subject'


# comments #####################################################################

class comments(RelationDefinition):
    subject = 'Comment'
    object = ('Patch', 'InsertionPoint')


# notification #################################################################

# XXX Comment should be in list, but this will conflict with the forge cube when
# using vcreview
class nosy_list(RelationDefinition):
    subject = ('Repository', 'Patch', 'Task',
               'VersionContent', 'DeletedVersionContent',
               'InsertionPoint')
    object = 'CWUser'

class interested_in(RelationDefinition):
    subject = 'CWUser'
    object = ('Repository', 'Patch')

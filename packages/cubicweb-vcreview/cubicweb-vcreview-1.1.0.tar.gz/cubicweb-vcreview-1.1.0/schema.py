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

from yams.buildobjs import (EntityType,
                            RelationDefinition,
                            String,
                            Int,
                            Boolean,
                            SubjectRelation)

from cubicweb.schema import (WorkflowableEntityType,
                             RQLConstraint,
                             RRQLExpression)

from cubes.vcsfile.schema import Repository


Repository.add_relation(Boolean(default=False, required=True),
                        name='has_review')

# the patch entity #############################################################


_SAME_REPO_CONSTRAINT = '''NOT EXISTS(
    S patch_revision RE,
    RE from_repository RO,
    O from_repository R,
    NOT R identity RO
)'''

class Patch(WorkflowableEntityType):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': (), # created by an internal session in a looping task
        'update': ('managers', 'users'),
        'delete': ('managers',),
        }
    patch_name = String(
        required=True,
        description=_('name of the patch in the repository'),
        fulltextindexed=True)
    patch_revision = SubjectRelation('Revision',
                                     __permissions__={
                                         'read': ('managers', 'users', 'guests'),
                                         'add': (), # created by an internal session in a looping task
                                         'delete': (),
                                         },
                                     constraints=[RQLConstraint(_SAME_REPO_CONSTRAINT)],
                                     cardinality='+?')


class repository_committer(RelationDefinition):
    """integrator (review level 2)"""
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers',),
        'delete': ('managers',),
        }
    subject = 'Repository'
    object = 'CWUser'

class repository_reviewer(RelationDefinition):
    """(review level 1)"""
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'committers',
                RRQLExpression('S repository_committer U')),
        'delete': ('managers', 'committers',
                   RRQLExpression('S repository_committer U')),
        }
    subject = 'Repository'
    object = 'CWUser'

class patch_reviewer(RelationDefinition):
    """The good fellow reviewing a single patch"""
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'committers',
                RRQLExpression('S patch_revision RE, RE from_repository R, R repository_committer U')),
        'delete': ('managers', 'committers',
                   RRQLExpression('S patch_revision RE, RE from_repository R, R repository_committer U')),
        }
    subject = 'Patch'
    object = 'CWUser'
    constraints = [RQLConstraint('EXISTS(O in_group G, G name "reviewers") '
                                 'OR EXISTS(S patch_revision RE, '
                                 '          RE from_repository R, '
                                 '          R repository_reviewer O)')]

class patch_committer(RelationDefinition):
    """The level 2 guy in charge of getting the patch published"""
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'committers',
                RRQLExpression('S patch_revision RE, RE from_repository R, R repository_committer U')),
        'delete': ('managers', 'committers',
                   RRQLExpression('S patch_revision RE, RE from_repository R, R repository_committer U')),
        }
    subject = 'Patch'
    object = 'CWUser'
    constraints = [RQLConstraint('EXISTS(O in_group G, G name "committers") '
                                 'OR EXISTS(S patch_revision RE, RE from_repository R, R repository_committer O)')]


class use_global_groups(RelationDefinition):
    """Use the ``reviewer`` global group to pick reviewer

    When false, only explicit reviewer set with ``repository_reviewer`` are
    taken in account.
    """
    subject = 'Repository'
    object = 'Boolean'
    cardinality = '11'
    default = True


# ability to reference diff chunks #############################################

class InsertionPoint(EntityType):
    """diff hunk"""
    __unique_together__ = [('lid', 'point_of')]
    lid = Int(indexed=True, required=True)

    point_of = SubjectRelation('Revision', cardinality = '1*',
                               composite = 'object', inlined = True)


# activities ###################################################################

class has_activity(RelationDefinition):
    subject = ('Patch', 'InsertionPoint')
    object = 'Task'
    cardinality = '*?'
    composite = 'subject'


# comments #####################################################################

class comments(RelationDefinition):
    subject = 'Comment'
    object = ('Task',)

# notification #################################################################

# XXX Comment should be in list, but this will conflict with the forge cube when
# using vcreview
class nosy_list(RelationDefinition):
    subject = ('Repository', 'Patch', 'Revision', 'Task', 'InsertionPoint')
    object = 'CWUser'

class interested_in(RelationDefinition):
    subject = 'CWUser'
    object = ('Repository', 'Patch')

# copyright 2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-vcreview entity's classes"""

from random import choice

from logilab.common.decorators import monkeypatch

from cubicweb.entities import AnyEntity
from cubicweb.view import EntityAdapter
from cubicweb.selectors import is_instance

from cubes.comment import entities as comment
from cubes.vcsfile import entities as vcsfile
from cubes.task import entities as task


class InsertionPoint(AnyEntity):
    __regid__ = 'InsertionPoint'
    @property
    def parent(self):
        return self.point_of[0]


class Patch(AnyEntity):
    __regid__ = 'Patch'

    def dc_title(self):
        return self.patch_name

    @property
    def repository(self):
        return self.patch_repository[0]

    @property
    def revisions(self):
        return sorted(self.patch_revision, key=lambda x: x.revision)

    def patch_files(self):
        return set(vc.file.path for vc in self.patch_revision)

    def tip(self):
        rset = self._cw.execute(
            'Any VC,R,RA,RB,RC,RD ORDERBY RC DESC LIMIT 1 '
            'WHERE X eid %(x)s, X patch_revision VC, VC from_revision R,'
            'R author RA, R branch RB, R creation_date RC, R description RD',
            {'x': self.eid})
        if rset:
            return rset.get_entity(0, 0)
        return None

    non_final_states = set( ('deleted', 'reviewed', 'pending-review', 'in-progress') )
    active_states = set( ('reviewed', 'pending-review', 'in-progress') )

    def is_active(self):
        return self.cw_adapt_to('IWorkflowable').state in self.active_states


@monkeypatch(vcsfile.DeletedVersionContent, 'patch')
@property
def patch(self):
    return self.reverse_patch_revision and self.reverse_patch_revision[0]


@monkeypatch(vcsfile.Repository, 'patchrepo_of')
@property
def patchrepo_of(self):
    return self.reverse_has_patch_repository and self.reverse_has_patch_repository[0]

@monkeypatch(vcsfile.Repository, 'patchrepo')
@property
def patchrepo(self):
    return self.has_patch_repository and self.has_patch_repository[0]

@monkeypatch(task.Task, 'activity_of')
@property
def activity_of(self):
    return self.reverse_has_activity and self.reverse_has_activity[0]


class CommentITreeAdapter(comment.CommentITreeAdapter):
    def path(self):
        path = super(CommentITreeAdapter, self).path()
        rootrset = self._cw.eid_rset(path[0])
        if rootrset.description[0][0] == 'InsertionPoint':
            path.insert(0, rootrset.get_entity(0, 0).parent.eid)
        return path


class PatchReviewBehaviour(EntityAdapter):
    __regid__ = 'IPatchReviewControl'
    __select__ = is_instance('Patch')

    def reviewers_rset(self):
        # ensure patch author can't review his own patch
        return self._cw.execute(
            'Any U WHERE EXISTS(U in_group G, G name "reviewers") '
            'OR EXISTS(P patch_repository R, R repository_reviewer U), '
            'NOT P created_by U, P eid %(p)s',
            {'p': self.entity.eid})

    def set_reviewers(self, transition):
        if self.entity.patch_reviewer:
            return
        # XXX only consider review affected during the last week by getting date
        # of the first in-progress -> pending-review transition? or use
        # something like a review_started_on attribute on patches ?
        nbpatches = dict(self._cw.execute(
            'Any U, COUNT(P) GROUPBY U WHERE P patch_reviewer U, '
            'P in_state S, S name IN ("in-progress", "pending-review")'))
        ueids = []
        mincount = None
        for ueid, in self.reviewers_rset():
            count = nbpatches.get(ueid, 0)
            if mincount is None:
                mincount = count
                ueids = [ueid]
            elif count < mincount:
                mincount = count
                ueids = [ueid]
            elif count == mincount:
                ueids.append(ueid)
        if ueids:
            self._cw.execute('SET P patch_reviewer U WHERE P eid %(p)s, U eid %(u)s',
                             {'p': self.entity.eid, 'u': choice(ueids)})


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (CommentITreeAdapter,))
    vreg.register_and_replace(CommentITreeAdapter, comment.CommentITreeAdapter)

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
"""cubicweb-vcreview entity's classes"""

from random import choice

from logilab.common.decorators import monkeypatch

from cubicweb.entities import AnyEntity
from cubicweb.view import EntityAdapter
from cubicweb.selectors import is_instance

from cubes.comment import entities as comment
from cubes.task import entities as task

from cubes.vcreview import users_by_author

class InsertionPoint(AnyEntity):
    __regid__ = 'InsertionPoint'
    @property
    def parent(self):
        return self.point_of[0]

_TIP_MOST_REVS = ('Any TIP, H '
                  'ORDERBY H ASC, TIP DESC'
                  'WHERE P eid %(p)s, '
                  '      P patch_revision TIP, '
                  '      TIP hidden H, '
                  '      NOT EXISTS(R obsoletes TIP, '
                  '                 P patch_revision R)')

class Patch(AnyEntity):
    __regid__ = 'Patch'

    def dc_title(self):
        return self.patch_name

    @property
    def repository(self):
        return self.patch_revision[0].from_repository[0]


    @property
    def revisions(self):
        return sorted(self.patch_revision, key=lambda x: x.revision)

    def patch_files(self):
        return set(vc.file.path for vc in self.patch_revision)

    def tip(self):
        return self._cw.entity_from_eid(self.all_tips()[0][0])

    def all_tips(self):
        return list(self._cw.execute(_TIP_MOST_REVS, {'p': self.eid}))

    final_states = set( ('folded', 'applied', 'rejected') )

    @property
    def is_final(self):
        return self.cw_adapt_to('IWorkflowable').state in self.final_states


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
            'DISTINCT Any U '
            'WHERE P eid %(p)s, '
            '      P patch_revision RE, '
            '      NOT P created_by U, '
            '      EXISTS(R use_global_groups TRUE, U in_group G, G name "reviewers") '
            '      OR EXISTS(RE from_repository R, '
            '                R repository_reviewer U)',
            {'p': self.entity.eid})

    def set_reviewers(self):
        if self.entity.patch_reviewer:
            return
        # look for patch authors, so we don't ask them to review their own patch
        authors = set()
        for rev in self.entity.patch_revision:
            authors.update(users_by_author(self._cw.execute, rev.author))

        # XXX only consider review affected during the last week by getting date
        # of the first in-progress -> pending-review transition? or use
        # something like a review_started_on attribute on patches ?
        nbpatches = dict(self._cw.execute(
            'Any U, COUNT(P) GROUPBY U WHERE P patch_reviewer U, '
            'P in_state S, S name IN ("in-progress", "pending-review")'))
        ueids = []
        mincount = None
        for ueid, in self.reviewers_rset():
            if ueid in authors:
                continue
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

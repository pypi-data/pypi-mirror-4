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

from __future__ import with_statement

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.server.session import security_enabled, hooks_control

class PatchReviewWorkflowTC(CubicWebTC):

    def setup_database(self):
        req = self.request()
        self.reviewer1 = self.create_user(req, 'reviewer1', ('users', 'reviewers'),
                                          email=u'reviewer1@cwo')
        self.reviewer2 = self.create_user(req, 'reviewer2', ('users', 'reviewers'),
                                          email=u'reviewer2@cwo')
        self.committer = self.create_user(req, 'committer', ('users',))
        session = self.session
        session.set_cnxset()
        with security_enabled(session, write=False):
            with hooks_control(session, session.HOOKS_DENY_ALL, 'metadata'):
                vcrepo = session.create_entity(
                    'Repository', repository_committer=self.committer)
                self.patch1eid = session.create_entity(
                    'Patch', patch_repository=vcrepo, originator=u'bob <reviewer1@cwo>').eid
                self.patch2eid = session.create_entity(
                    'Patch', patch_repository=vcrepo, originator=u'bob <reviewer1@cwo>').eid
                session.commit(free_cnxset=False)
                self.task1eid = session.create_entity(
                    'Task', reverse_has_activity=self.patch1eid, title=u'todo 1').eid

    def test_wf(self):
        req = self.request()
        patch = req.execute('Any X WHERE X eid %(x)s', {'x': self.patch1eid}).get_entity(0, 0)
        self.assertFalse(patch.patch_reviewer)
        self.assertTrue(self.reviewer1.eid in [u.eid for u in patch.created_by])
        self.assertTrue(self.reviewer1.eid in [u.eid for u in patch.owned_by])
        patch.cw_adapt_to('IWorkflowable').fire_transition('ask review')
        self.commit()
        patch.cw_clear_all_caches()
        self.assertEqual(patch.patch_reviewer[0].eid, self.reviewer2.eid)
        with self.login('reviewer1'):
            req = self.request()
            rset = req.execute('Any X WHERE X eid %(x)s', {'x': self.patch1eid})
            self.assertListEqual(sorted(x[0] for x in self.action_submenu(req, rset, 'workflow')),
                                 ['accept', 'ask rework', 'fold', 'view history', 'view workflow'])
            # reviewer1 submit its second patch for review: while reviewer2
            # already has a patch for review, it should be picked anyway as a
            # patch creator can't be its reviewer
            patch = req.execute('Any X WHERE X eid %(x)s', {'x': self.patch2eid}).get_entity(0, 0)
            self.assertFalse(patch.patch_reviewer)
            patch.cw_adapt_to('IWorkflowable').fire_transition('ask review')
            self.commit()
            patch.cw_clear_all_caches()
            self.assertEqual(patch.patch_reviewer[0].eid, self.reviewer2.eid)
            # create a task and mark the task1 as done
            task2eid = req.create_entity(
                'Task', reverse_has_activity=patch, title=u'todo 2').eid
            task = req.execute('Any X WHERE X eid %(x)s', {'x': self.task1eid}).get_entity(0, 0)
            task.cw_adapt_to('IWorkflowable').fire_transition('done')
            self.commit()
        with self.login('reviewer2'):
            req = self.request()
            rset = req.execute('Any X WHERE X eid %(x)s', {'x': self.patch1eid})
            self.assertListEqual(sorted(x[0] for x in self.action_submenu(req, rset, 'workflow')),
                                 ['accept', 'ask rework', 'fold', 'view history', 'view workflow'])
            patch = rset.get_entity(0, 0)
            patch.cw_adapt_to('IWorkflowable').fire_transition('accept')
            self.commit()
            patch.cw_clear_all_caches()
            self.assertListEqual(sorted(x[0] for x in self.action_submenu(req, rset, 'workflow')),
                                 [u'ask review', u'ask rework', u'fold', u'view history', u'view workflow'])
            # create a task and mark task2 as done
            task3eid = req.create_entity(
                'Task', reverse_has_activity=patch, title=u'todo 3').eid
            task = req.execute('Any X WHERE X eid %(x)s', {'x': task2eid}).get_entity(0, 0)
            task.cw_adapt_to('IWorkflowable').fire_transition('done')
            self.commit()
        with self.login('committer'):
            req = self.request()
            rset = req.execute('Any X WHERE X eid %(x)s', {'x': self.patch1eid})
            self.assertListEqual(sorted(x[0] for x in self.action_submenu(req, rset, 'workflow')),
                                 ['apply', 'ask review', 'ask rework', 'fold', 'reject', 'view history', 'view workflow'])
            patch = rset.get_entity(0, 0)
            patch.cw_adapt_to('IWorkflowable').fire_transition('apply')
            self.commit()
            patch.cw_clear_all_caches()
            self.assertListEqual(sorted(x[0] for x in self.action_submenu(req, rset, 'workflow')),
                                 ['view history'])
            # mark task3 as done
            task = req.execute('Any X WHERE X eid %(x)s', {'x': task3eid}).get_entity(0, 0)
            task.cw_adapt_to('IWorkflowable').fire_transition('done')
            self.commit()



if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

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

from __future__ import with_statement

import os.path as osp
import functools
import tempfile
import tarfile
from shutil import rmtree

from logilab.common.decorators import classproperty

from cubicweb.devtools.testlib import CubicWebTC

from cubes.vcsfile.testutils import init_vcsrepo

class PatchReviewWorkflowTC(CubicWebTC):

    @classmethod
    def setUpClass(cls):
        cls.__tmpdir = tempfile.mkdtemp(prefix='vcreview-test-')
        tarfile.open(cls.repo_path + '.tar').extractall(cls.__tmpdir)

    @classmethod
    def tearDownClass(cls):
        cls.cleanup()

    @classmethod
    def cleanup(cls):
        try:
            rmtree(cls.__tmpdir)
        except:
            pass

    @classproperty
    def full_repo_path(cls):
        return osp.join(cls.__tmpdir, u'repo')

    def setup_database(self):
        req = self.request()
        create_user = functools.partial(self.create_user, req)
        self.reviewer1 = create_user('Victor', ('users', 'reviewers'),
                                     email=u'victor@ratax.es')
        self.reviewer2 = create_user('Podular', ('users', 'reviewers'),
                                     email=u'podular@elephan.tz')
        self.committer = create_user('committer', ('users',))
        with self.session.security_enabled(write=False):
            with self.session.deny_all_hooks_but('metadata'):
                req.create_entity('Repository', type=u'mercurial',
                                  encoding=u'utf8',
                                  path=self.full_repo_path,
                                  repository_committer=self.committer,
                                  has_review=True)
                self.commit()
                init_vcsrepo(self.repo)
                rset = req.execute('Patch P ORDERBY P DESC '
                                   'WHERE P in_state S, '
                                   '      S name "pending-review"')
                self.patch1eid = rset[1][0]
                self.patch2eid = rset[2][0]
                self.commit()
                self.task1eid = req.create_entity(
                    'Task', reverse_has_activity=self.patch1eid, title=u'todo 1').eid
        self.commit()

    def test_wf(self):
        req = self.request()
        patch = req.entity_from_eid(self.patch1eid)
        self.assertEqual(patch.patch_reviewer[0].eid, self.reviewer2.eid)
        with self.login('Victor'):
            req = self.request()
            rset = req.execute('Any X WHERE X eid %(x)s', {'x': self.patch1eid})
            self.assertListEqual(sorted(x[0] for x in self.action_submenu(req, rset, 'workflow')),
                                 ['accept', 'ask rework', 'fold', 'view history', 'view workflow'])
            # reviewer1 submit its second patch for review: while reviewer2
            # already has a patch for review, it should be picked anyway as a
            # patch creator can't be its reviewer
            patch = req.execute('Any X WHERE X eid %(x)s', {'x': self.patch2eid}).get_entity(0, 0)
            self.assertEqual(patch.patch_reviewer[0].eid, self.reviewer2.eid)
            # create a task and mark the task1 as done
            task2eid = req.create_entity(
                'Task', reverse_has_activity=patch, title=u'todo 2').eid
            task = req.execute('Any X WHERE X eid %(x)s', {'x': self.task1eid}).get_entity(0, 0)
            task.cw_adapt_to('IWorkflowable').fire_transition('done')
            self.commit()
        with self.login('Podular'):
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


    def test_review_adapter_reviewers_rset(self):
        """check reviewer configuration

        1) Test that explicit `repository_reviewer` are taken in account
        2) Test that `reviewer` group can be disabled on a repo.
        """
        req = self.request()
        req.execute('SET X repository_reviewer U WHERE U login "committer"')
        patch = req.entity_from_eid(self.patch1eid)
        ireview = patch.cw_adapt_to('IPatchReviewControl')
        self.assertEqual(set(x for x, in ireview.reviewers_rset().rows),
                         set([self.reviewer2.eid,
                              self.committer.eid]))
        req.execute('SET X use_global_groups FALSE')
        patch.cw_clear_all_caches()
        ireview = patch.cw_adapt_to('IPatchReviewControl')
        self.assertEqual(set(x for x, in ireview.reviewers_rset().rows),
                         set([self.committer.eid]))


PatchReviewWorkflowTC.repo_path = osp.join(PatchReviewWorkflowTC.datadir,
                                      u'demo-repo-final')



if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

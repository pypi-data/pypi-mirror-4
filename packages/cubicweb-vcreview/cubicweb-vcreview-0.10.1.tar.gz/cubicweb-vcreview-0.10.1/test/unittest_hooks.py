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

from os import path as osp
from shutil import rmtree
import re

from logilab.common.shellutils import unzip
from logilab.common.testlib import mock_object

from cubicweb.devtools.testlib import MAILBOX, CubicWebTC

from cubes.vcsfile.testutils import init_vcsrepo
from cubes.vcreview import hooks

def revnums(patch):
    return sorted(vc.revision for vc in patch.patch_revision)


class PatchCreationHooksTC(CubicWebTC):
    _repo_path = u'patchrepo'
    repo_title = u'patch repository'

    @classmethod
    def setUpClass(cls):
        cls.cleanup()
        unzip(cls.repo_path + '.zip', cls.datadir)

    @classmethod
    def tearDownClass(cls):
        cls.cleanup()

    @classmethod
    def cleanup(cls):
        try:
            rmtree(cls.repo_path)
        except:
            pass

    def setUp(self):
        super(PatchCreationHooksTC, self).setUp()
        # XXX do this in setUp instead of setup_database else mailbox is reseted
        # while this test check notifications
        req = self.request()
        assert req.execute('INSERT EmailAddress E: E address "admin@cwo", U primary_email E '
                    'WHERE U login "admin"')
        self.vcsrepo = self._create_repo(req)
        self.reviewer1 = self.create_user(req, 'bob', ('users', 'reviewers'),
                                          email=u'bob@cwo')
        self.commit()
        from cubicweb.server import hook
        from cubicweb.predicates import on_fire_transition
        class ForceReviewerHook(hook.Hook):
            __regid__ = 'vcreview.test.forcereviewer'
            __select__ = hook.Hook.__select__ & on_fire_transition('Patch', 'ask review')
            events = ('after_add_entity',)
            def __call__(self):
                patch = self.entity.for_entity
                self._cw.execute('SET P patch_reviewer U WHERE P eid %(p)s, U login "admin"',
                                 {'p': patch.eid, 'u': self._cw.user.eid})

        with self.temporary_appobjects(ForceReviewerHook):
            init_vcsrepo(self.repo)
            self.commit()

    def _create_repo(self, req):
        vcsrepo = req.create_entity(
            'Repository', type=u'mercurial', encoding=u'utf-8',
            import_revision_content=True,
            path=self.repo_path, title=self.repo_title)
        # circular relations, only to make it think it is a patch repository
        vcsrepo.set_relations(has_patch_repository=vcsrepo,
                              repository_reviewer=req.user)
        return vcsrepo

    def assertMatches(self, got, expected):
        """ expected is a regular expression """
        self.assertTrue(re.match(expected, got),
                        '%r\n does not match:\n %r' % (got, expected))

    def assertEmailEqual(self, email, subject, recipient, content):
        self.assertEqual(email.subject, subject)
        self.assertEqual(email.recipients, [recipient])
        self.assertMatches(email.content, content)

    def test_imported_patches(self):
        patches = self.execute('Patch X ORDERBY X')
        # test base patch creation #############################################
        byfile = {}
        bypatch = {}
        for patch in patches.entities():
            files = patch.patch_files()
            self.assertTrue(patch.patch_name in files)
            if len(files) == 1:
                byfile.setdefault(iter(files).next(), []).append(patch)
            else:
                bypatch[patch] = files
        self.assertEqual(len(byfile), 6, byfile)
        # bypatch check we're correctly following renaming
        self.assertEqual(len(bypatch), 1)
        self.assertEqual(len(patches), 9)

        folded = bypatch.keys()[0]
        self.assertEqual(folded.cw_adapt_to('IWorkflowable').state, 'folded')

        self.assertEqual(len(byfile['patch1.diff']), 2)
        patch1_1 = byfile['patch1.diff'][0]
        self.assertEqual(patch1_1.cw_adapt_to('IWorkflowable').state, 'deleted')
        self.assertEqual(revnums(patch1_1), [0, 1])
        patch1_2 = byfile['patch1.diff'][1]
        self.assertEqual(patch1_2.cw_adapt_to('IWorkflowable').state, 'deleted')
        self.assertEqual(revnums(patch1_2), [7, 8, 9])

        self.assertEqual(len(byfile['patch2.diff']), 1)
        patch2 = byfile['patch2.diff'][0]
        self.assertEqual(patch2.cw_adapt_to('IWorkflowable').state, 'deleted')
        self.assertEqual(revnums(patch2), [0, 1, 2, 5, 6])

        self.assertEqual(len(byfile['patch3.diff']), 2)
        patch3_1 = byfile['patch3.diff'][0]
        self.assertEqual(patch3_1.cw_adapt_to('IWorkflowable').state, 'deleted')
        self.assertEqual(revnums(patch3_1), [3, 4])
        patch3_2 = byfile['patch3.diff'][1]
        history = patch3_2.cw_adapt_to('IWorkflowable').workflow_history
        self.assertEqual(history[-1].previous_state.name, 'pending-review')
        self.assertEqual(history[-1].new_state.name, 'rejected')
        self.assertEqual(revnums(patch3_2), [7, 10, 15])

        self.assertEqual(len(byfile['patch4.diff']), 1)
        patch4 = byfile['patch4.diff'][0]
        self.assertEqual(patch4.cw_adapt_to('IWorkflowable').state, 'in-progress')
        self.assertEqual(revnums(patch4), [17, 18, 19])
        history = patch4.cw_adapt_to('IWorkflowable').workflow_history
        self.assertEqual(history[-1].previous_state.name, 'pending-review')
        self.assertEqual(history[-1].new_state.name, 'in-progress')

        # test nosy-list / notifications #######################################
        self.assertTrue(patch3_2.nosy_list)
        self.assertTrue(patch4.nosy_list)
        self.assertEqual(len(MAILBOX), 8, (len(MAILBOX), MAILBOX))

        self.assertEmailEqual(MAILBOX[0],
                              '[patch repository] patch pending-review: patch3.diff',
                              'admin@cwo',
                              u'''
cubicweb changed status from <in-progress> to <pending-review> for entity
'patch3.diff'

review asked by Sylvain Th.*nault <sylvain.thenault@logilab.fr> in
#10:9cf50f15d9a7

url: http://testing.fr/cubicweb/patch/%s\n''' % patch3_2.eid)

        self.assertEmailEqual(MAILBOX[1],
                              '[patch repository] patch assigned: patch3.diff',
                              'admin@cwo',
                              u'''
You have been assigned for review of patch patch3.diff

url: http://testing.fr/cubicweb/patch/%s\n''' % patch3_2.eid)

        self.assertEmailEqual(MAILBOX[2],
                              '[patch repository] patch rejected: patch3.diff',
                              'admin@cwo',
                              u'''
cubicweb changed status from <pending-review> to <rejected> for entity
'patch3.diff'

rejected by Sylvain Th.*nault <sylvain.thenault@logilab.fr> in #15:0fc9a74c0ce9

url: http://testing.fr/cubicweb/patch/%s\n''' % patch3_2.eid)

        self.assertEmailEqual(MAILBOX[3],
                              '[patch repository] patch pending-review: patch4.diff',
                              'admin@cwo',
                              u'''
cubicweb changed status from <in-progress> to <pending-review> for entity
'patch4.diff'

review asked by Bob Cornelieus <bob@cwo> in #17:f45b1e15a66e

url: http://testing.fr/cubicweb/patch/%s\n''' % patch4.eid)

        self.assertEmailEqual(MAILBOX[4],
                              '[patch repository] patch pending-review: patch4.diff',
                              'bob@cwo',
                              u'''
cubicweb changed status from <in-progress> to <pending-review> for entity
'patch4.diff'

review asked by Bob Cornelieus <bob@cwo> in #17:f45b1e15a66e

url: http://testing.fr/cubicweb/patch/%s\n''' % patch4.eid)

        self.assertEmailEqual(MAILBOX[5],
                         '[patch repository] patch assigned: patch4.diff',
                              'admin@cwo',
                              u'''
You have been assigned for review of patch patch4.diff

url: http://testing.fr/cubicweb/patch/%s\n''' % patch4.eid)

        self.assertEmailEqual(MAILBOX[6],
                              '[patch repository] patch in-progress: patch4.diff',
                              'admin@cwo',
                              u'''
cubicweb changed status from <pending-review> to <in-progress> for entity
'patch4.diff'

modified by Julien Cristau <julien.cristau@logilab.fr> in #19:0a504eb04e48

url: http://testing.fr/cubicweb/patch/%s\n''' % patch4.eid)

        MAILBOX[:] = ()
        req = self.request()
        req.create_entity('Task', title=u'todo', reverse_has_activity=patch3_2)
        done = req.create_entity('Task', title=u'done', reverse_has_activity=patch3_2)
        self.commit()
        self.assertEqual(len(MAILBOX), 2)
        self.assertEmailEqual(MAILBOX[1],
                              '[patch repository] patch task: patch3.diff - done',
                              'admin@cwo',
                              u'''
done



url: http://testing.fr/cubicweb/task/%s\n''' % done.eid)

        MAILBOX[:] = ()
        done.cw_adapt_to('IWorkflowable').fire_transition('done')
        self.commit()
        self.assertEqual(MAILBOX, [])

        # force state
        patch3_2.cw_adapt_to('IWorkflowable').change_state('pending-review')
        self.commit()

        MAILBOX[:] = ()

        patch3_2.cw_adapt_to('IWorkflowable').fire_transition('accept')
        self.commit()

        # fake revision from the main repo of our patch repo
        atrevision = [self.session.entity_from_eid(patch3_2.revisions[-1].eid)]
        revision = mock_object(repository=self.vcsrepo,
                               description='applied patch patch3.diff',
                               author='syt',
                               eid=patch3_2.revisions[-1].rev.eid,
                               reverse_at_revision=atrevision,
                               reverse_from_revision=atrevision)
        # hi-hack vcsrepo._cw to avoid connections pool pb
        self.vcsrepo._cw = self.session
        self.session.set_cnxset()
        op = hooks.SearchPatchStateInstructionOp.get_instance(self.session)
        op.add_data(revision)
        self.commit() # will process our fake operation
        patch3_2.cw_clear_all_caches()
        self.assertEqual(patch3_2.cw_adapt_to('IWorkflowable').state, 'applied')
        #self.assertEqual(patch3_2.applied_at[0].eid, patch3_2.revisions[-1].rev.eid) XXX

        self.assertEqual(len(MAILBOX), 2, MAILBOX)
        self.assertEmailEqual(MAILBOX[0],
                              '[patch repository] patch reviewed: patch3.diff',
                              'admin@cwo',
                              '''
admin changed status from <pending-review> to <reviewed> for entity
'patch3.diff'



remaining tasks:

- todo

url: http://testing.fr/cubicweb/patch/%s\n''' % patch3_2.eid)
        self.assertEmailEqual(MAILBOX[1],
                              '[patch repository] patch applied: patch3.diff',
                              'admin@cwo',
                              u'''
admin changed status from <reviewed> to <applied> for entity
'patch3.diff'

applied by syt

remaining tasks:

- todo

url: http://testing.fr/cubicweb/patch/%s\n''' % patch3_2.eid)

        self.vcsrepo._cw = self.request()

        # other meta-data ######################################################
        # mime type enforcements for special files
        self.assertEqual(
            self.vcsrepo.versioned_file('', 'patch_no_ext').head.data_format,
            'text/x-diff')
        self.assertEqual(
            self.vcsrepo.versioned_file('', 'series').head.data_format,
            'text/plain')
        self.assertEqual(
            self.vcsrepo.versioned_file('', 'README').head.data_format,
            'text/plain')
        # author from patch content
        self.assertEqual(folded.originator, 'The Patch Author <admin@cwo>')
        self.assertEqual(folded.creator.login, 'admin')
        # author from email
        patch = byfile['patch4.diff'][0]
        self.assertEqual(patch.originator, 'Bob Cornelieus <bob@cwo>')
        self.assertEqual(patch.creator.login, 'bob')
        # unmatched user
        patch = byfile['patch1.diff'][0]
        self.assertMatches(patch.originator, u'Sylvain Th.*nault <sylvain.thenault@logilab.fr>')
        self.assertEqual(patch.creator, None)

        # check email match is case-insensitive
        patch = byfile['patch5.diff'][0]
        self.assertEqual(patch.creator.login, 'bob')

PatchCreationHooksTC.repo_path = osp.join(PatchCreationHooksTC.datadir, u'patchrepo')

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

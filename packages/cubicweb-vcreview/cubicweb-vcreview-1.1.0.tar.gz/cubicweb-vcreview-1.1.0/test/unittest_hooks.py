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
import tempfile
import tarfile
from subprocess import check_call, Popen, PIPE

from logilab.common.decorators import classproperty

from cubicweb.devtools.testlib import MAILBOX, CubicWebTC

from cubes.vcsfile import bridge

from cubes.vcsfile.testutils import init_vcsrepo

def revnums(patch):
    return sorted(vc.revision for vc in patch.patch_revision)



class HgHelper(CubicWebTC):

    verbose_hg = False

    def setup_database(self):
        self.tmprepo = tempfile.mkdtemp()
        check_call(['hg', 'init', self.tmprepo])
        self.cwhgrepo = self.session.create_entity('Repository',
                                                  type=u'mercurial',
                                                  encoding=u'utf-8',
                                                  import_revision_content=True,
                                                  path=unicode(self.tmprepo),
                                                  has_review=True)
        self.refresh()
        self.session.commit(free_cnxset=False)

    def tearDown(self):
        bridge._REPOHDLRS.clear()
        rmtree(self.tmprepo, ignore_errors=True)
        repo = getattr(self, 'cwhgrepo', None)
        if getattr(repo, 'local_cache', None) is not None:
            rmtree(repo.local_cache, ignore_errors=True)
        return super(HgHelper, self).tearDown()

    def call_hg(self, *args):
        """Call a mercurial command in the repo"""
        kwargs = {}
        if self.verbose_hg:
            print ' '.join(args)
        else:
            devnull = open('/dev/null', 'a')
            kwargs['stdout'] = devnull
            kwargs['stderr'] = devnull
        check_call(['hg', '-R', self.tmprepo] + list(args), **kwargs)

    def append_to(self, path, content):
        """Add a new line to a file in the repo"""
        path = osp.join(self.tmprepo, path)
        with open(path, 'a') as f:
            f.write(content)
            f.write('\n')

    def refresh(self):
        """Have cubicweb read the on disk repo"""
        with self.repo.internal_session() as session:
            bridge.import_content(session, raise_on_error=True)
            session.commit()

    def all_revs(self):
        """Return all revisions that exist in the test repo entity"""
        rql = 'Revision R ORDERBY R WHERE R from_repository RE, RE eid %(re)s'
        rset = self.execute(rql, {'re': self.cwhgrepo.eid})
        return list(rset.entities())

    def get_id(self, rev):
        """return the full hex of the full id of a changeset"""
        cmd = ['hg', '-R', self.tmprepo, 'id', '--debug', '--id', '--rev', rev]
        if self.verbose_hg:
            print ' '.join(cmd[3:])
        child = Popen(cmd, stdout=PIPE)
        rid, _ = child.communicate()
        rid = rid.strip()
        assert len(rid) == 40, rid
        return rid

    @staticmethod
    def get_wf_history(patch):
        return [tr.new_state.name
                for tr in patch.cw_adapt_to('IWorkflowable').workflow_history]

class PatchLifeCycleTC(HgHelper):

    def test_root_publishing(self):

        hg = self.call_hg
        a = self.append_to

        ### 1) root initially draft becomes public
        #############################################################

        # create a simple root changeset as draft
        a('jungle', 'Babar')
        hg('add', osp.join(self.tmprepo, 'jungle'))
        hg('commit', '-m', 'Initial jungle content')
        self.refresh()

        # We should have a new Patch linked to revision 0
        revs = self.all_revs()
        self.assertEqual(1, len(revs))
        self.assertTrue(revs[0].reverse_patch_revision)
        patch = revs[0].reverse_patch_revision[0]
        self.assertEqual('Initial jungle content', patch.patch_name)
        patch_state = patch.cw_adapt_to('IWorkflowable').state
        self.assertEqual('pending-review', patch_state)
        wf_history = self.get_wf_history(patch)
        self.assertEqual(['pending-review'], wf_history)

        # turn the changeset public
        hg('phase', '--public', '0')
        self.refresh()
        # check that the patch has been "applied"
        patch.cw_clear_all_caches()
        patch_state = patch.cw_adapt_to('IWorkflowable').state
        self.assertEqual('applied', patch_state)
        wf_history = self.get_wf_history(patch)
        self.assertEqual(['pending-review', 'applied'], wf_history)

    def test_draft_publishing(self):
        self.test_root_publishing()
        hg = self.call_hg
        a = self.append_to

        oldpatch = self.all_revs()[0].reverse_patch_revision[0]

        ### 2) draft changeset becomes public
        #############################################################

        # create a draft child
        a('jungle', 'Celestine')
        hg('commit', '-m', 'couple of elephants')
        self.refresh()

        # We should have a new Patch linked to revision 1
        for rev in self.all_revs():
            if rev.description == 'couple of elephants':
                break
        else:
            self.fail('missing draft child')
        self.assertTrue(rev.reverse_patch_revision)
        patch = rev.reverse_patch_revision[0]
        self.assertNotEqual(oldpatch.eid, patch.eid)
        self.assertEqual('couple of elephants', patch.patch_name)
        patch_state = patch.cw_adapt_to('IWorkflowable').state
        self.assertEqual('pending-review', patch_state)
        wf_history = self.get_wf_history(patch)
        self.assertEqual(['pending-review'], wf_history)
        # old patch is unchanged
        oldpatch_state = oldpatch.cw_adapt_to('IWorkflowable').state
        self.assertEqual('applied', oldpatch_state)

        # make the child public
        hg('phase', '--public', '1')
        self.refresh()
        patch.cw_clear_all_caches()
        # check that the patch has been "applied"
        patch_state = patch.cw_adapt_to('IWorkflowable').state
        self.assertEqual('applied', patch_state)
        wf_history = self.get_wf_history(patch)
        self.assertEqual(['pending-review', 'applied'], wf_history)

    def test_simple_amend(self):
        self.test_root_publishing()
        hg = self.call_hg
        a = self.append_to
        oldpatch = self.all_revs()[0].reverse_patch_revision[0]

        ### 3) simple amend that ends up published
        #############################################################

        # add a new draft children again
        a('jungle', 'Pam')
        hg('commit', '-m', 'fisrt child')  # sic
        self.refresh()

        # We should have a new Patch linked to revision 1
        rev = self.all_revs()[-1]
        assert rev.description == 'fisrt child'
        self.assertTrue(rev.reverse_patch_revision)
        patch = rev.reverse_patch_revision[0]
        self.assertNotEqual(oldpatch.eid, patch.eid)
        self.assertEqual('fisrt child', patch.patch_name)
        patch_state = patch.cw_adapt_to('IWorkflowable').state
        self.assertEqual('pending-review', patch_state)
        wf_history = self.get_wf_history(patch)
        self.assertEqual(['pending-review'], wf_history)

        # Fix changeset content
        path = osp.join(self.tmprepo, 'jungle')
        with open(path, 'r') as f:
            data = f.read().replace('Pam', 'Pom')
        with open(path, 'w') as f:
            f.write(data)
        hg('commit', '--amend', '-m', 'firts child')
        self.refresh()
        # test that the new revision is added to the same patch
        patch.cw_clear_all_caches()
        rev = self.all_revs()[-1]
        assert rev.description == 'firts child'
        newpatch = rev.reverse_patch_revision[0]
        self.assertEqual(patch.eid, newpatch.eid)
        patch_state = patch.cw_adapt_to('IWorkflowable').state
        self.assertEqual('pending-review', patch_state)
        wf_history = self.get_wf_history(patch)
        self.assertEqual(['pending-review'], wf_history)

        # yet another successor. A public one
        hg('commit', '--amend', '-m', 'first child')
        hg('phase', '--public', '.')
        self.refresh()
        patch.cw_clear_all_caches()
        # check that the patch has been "applied"
        patch_state = patch.cw_adapt_to('IWorkflowable').state
        self.assertEqual('applied', patch_state)
        wf_history = self.get_wf_history(patch)
        self.assertEqual(['pending-review', 'applied'], wf_history)
        self.assertEqual(3, len(patch.patch_revision))


    def test_prune(self):
        self.test_root_publishing()
        hg = self.call_hg
        a = self.append_to
        oldpatch = self.all_revs()[0].reverse_patch_revision[0]

        ### 4) simple amend that ends up pruned
        #############################################################

        # add a new draft child again
        a('jungle', 'Zephir')
        hg('commit', '-m', 'seocnd child')  # sic
        self.refresh()

        # look for a new patch
        rev = self.all_revs()[-1]
        assert rev.description == 'seocnd child'
        self.assertTrue(rev.reverse_patch_revision)
        patch = rev.reverse_patch_revision[0]
        self.assertNotEqual(oldpatch.eid, patch.eid)
        self.assertEqual('seocnd child', patch.patch_name)
        patch_state = patch.cw_adapt_to('IWorkflowable').state
        self.assertEqual('pending-review', patch_state)
        wf_history = self.get_wf_history(patch)
        self.assertEqual(['pending-review'], wf_history)

        # amend the patch
        hg('commit', '--amend', '-m', 'second child')
        self.refresh()
        # test that patch has two revisions
        patch.cw_clear_all_caches()
        patch_state = patch.cw_adapt_to('IWorkflowable').state
        self.assertEqual('pending-review', patch_state)
        self.assertEqual(2, len(patch.patch_revision))
        wf_history = self.get_wf_history(patch)
        self.assertEqual(['pending-review'], wf_history)

        prec = self.get_id('.')
        hg('up', '.^')
        hg('debugobsolete', prec)  # Zephir is a monkey, donkey!
        self.refresh()
        # patch should turn rejected
        patch.cw_clear_all_caches()
        patch_state = patch.cw_adapt_to('IWorkflowable').state
        self.assertEqual('rejected', patch_state)
        wf_history = self.get_wf_history(patch)
        self.assertEqual(['pending-review', 'rejected'], wf_history)
        self.assertEqual(2, len(patch.patch_revision))

    def test_zombie(self):
        self.test_root_publishing()
        hg = self.call_hg
        a = self.append_to
        oldpatch = self.all_revs()[0].reverse_patch_revision[0]

        ### 5) changesets turning zombie at some point
        #############################################################

        # create a new draft child
        a('jungle', 'Flare')
        hg('commit', '-m', 'second child')
        self.refresh()

        # look for a new patch
        rev = self.all_revs()[-1]
        assert rev.description == 'second child'
        self.assertTrue(rev.reverse_patch_revision)
        patch = rev.reverse_patch_revision[0]
        self.assertNotEqual(oldpatch.eid, patch.eid)
        self.assertEqual('second child', patch.patch_name)
        patch_state = patch.cw_adapt_to('IWorkflowable').state
        self.assertEqual('pending-review', patch_state)
        wf_history = self.get_wf_history(patch)
        self.assertEqual(['pending-review'], wf_history)

        # have a successor out of the repo
        path = osp.join(self.tmprepo, 'jungle')
        with open(path, 'r') as f:
            data = f.read().replace('Flare', 'Flore')
        with open(path, 'w') as f:
            f.write(data)
        bundlepath = osp.join(self.tmprepo, 'flore.hg')
        hg('commit', '--amend', '-m', 'second child')
        hg('bundle', '-r', '.', '--base', '.^', bundlepath)
        hg('--config', 'extensions.mq=', 'strip', '.')
        self.refresh()
        # patch should be "outdated"
        patch.cw_clear_all_caches()
        patch_state = patch.cw_adapt_to('IWorkflowable').state
        self.assertEqual('outdated', patch_state)
        wf_history = self.get_wf_history(patch)
        self.assertEqual(['pending-review', 'outdated'], wf_history)
        self.assertEqual(1, len(patch.patch_revision))

        # make the successor visible again
        hg('unbundle', bundlepath)
        self.refresh()
        # test should be alive again
        patch.cw_clear_all_caches()
        patch_state = patch.cw_adapt_to('IWorkflowable').state
        self.assertEqual('pending-review', patch_state)
        wf_history = self.get_wf_history(patch)
        self.assertEqual(['pending-review', 'outdated', 'pending-review'],
                         wf_history)
        self.assertEqual(2, len(patch.patch_revision))

    def test_delete_revision(self):
        self.test_root_publishing()
        hg = self.call_hg
        a = self.append_to
        oldpatch = self.all_revs()[0].reverse_patch_revision[0]
        # create a new draft child
        a('jungle', 'Flare')
        hg('commit', '-m', 'second child')
        self.refresh()

        rev = self.all_revs()[-1]
        assert rev.description == 'second child'
        self.assertTrue(rev.reverse_patch_revision)
        eid_patch = rev.reverse_patch_revision[0].eid
        with self.repo.internal_session() as session:
            self.assertTrue(session.execute('DELETE Revision R WHERE R eid %(eid)s',
                                            {'eid': rev.eid}))
            session.commit()
        self.assertFalse(self.execute('Patch P WHERE P eid %(eid)s',
                                      {'eid': eid_patch}))

    def test_split(self):
        self.test_root_publishing()
        hg = self.call_hg
        a = self.append_to
        oldpatch = self.all_revs()[0].reverse_patch_revision[0]

        ### 6) split
        #############################################################

        # create a new draft changeset with two changes
        a('jungle', 'Alexandre')
        a('jungle', 'Isabelle')
        hg('commit', '-m', 'Moar children')
        self.refresh()

        # search for a new patch
        rev = self.all_revs()[-1]
        assert rev.description == 'Moar children'
        self.assertTrue(rev.reverse_patch_revision)
        patch = rev.reverse_patch_revision[0]
        self.assertNotEqual(oldpatch.eid, patch.eid)
        self.assertEqual('Moar children', patch.patch_name)
        patch_state = patch.cw_adapt_to('IWorkflowable').state
        self.assertEqual('pending-review', patch_state)
        wf_history = self.get_wf_history(patch)
        self.assertEqual(['pending-review'], wf_history)

        # split them in two
        hg('up', '.^')
        a('jungle', 'Alexandre')
        hg('commit', '-m', 'third child')
        a('jungle', 'Isabelle')
        hg('commit', '-m', 'fourth child')
        prec = self.get_id('-3')
        suc1 = self.get_id('-2')
        suc2 = self.get_id('-1')
        hg('debugobsolete', prec, suc1, suc2)
        self.refresh()
        # we should now have two patches
        patch.cw_clear_all_caches()
        suc1 = self.all_revs()[-2]
        suc2 = self.all_revs()[-1]
        assert suc1.description == 'third child'
        assert suc2.description == 'fourth child'
        self.assertTrue(suc1.reverse_patch_revision)
        self.assertTrue(suc2.reverse_patch_revision)
        patch1 = suc1.reverse_patch_revision[0]
        patch2 = suc2.reverse_patch_revision[0]
        self.assertEqual(patch.eid, patch1.eid)
        self.assertNotEqual(patch.eid, patch2.eid)
        self.assertEqual(2, len(patch1.patch_revision))
        self.assertEqual(1, len(patch2.patch_revision))
        patch1_state = patch1.cw_adapt_to('IWorkflowable').state
        self.assertEqual('pending-review', patch1_state)
        patch1_wf_history = self.get_wf_history(patch1)
        self.assertEqual(['pending-review'], patch1_wf_history)
        patch2_state = patch1.cw_adapt_to('IWorkflowable').state
        self.assertEqual('pending-review', patch2_state)
        patch2_wf_history = self.get_wf_history(patch2)
        self.assertEqual(['pending-review'], patch2_wf_history)

    def test_fold(self):
        self.test_root_publishing()
        hg = self.call_hg
        a = self.append_to

        ### 7) fold
        #############################################################
        # create two draft changesets
        a('jungle', 'Cornelius')
        hg('commit', '-m', 'counselor')
        a('jungle', 'Pompadour')
        hg('commit', '-m', 'More counselor')
        self.refresh()
        # test we have two distinct patches
        rev1 = self.all_revs()[-2]
        rev2 = self.all_revs()[-1]
        assert rev1.description == 'counselor'
        assert rev2.description == 'More counselor'
        self.assertTrue(rev1.reverse_patch_revision)
        self.assertTrue(rev2.reverse_patch_revision)
        patch1 = rev1.reverse_patch_revision[0]
        patch2 = rev2.reverse_patch_revision[0]
        self.assertNotEqual(patch1.eid, patch2.eid)

        # fold the two changesets
        hg('update', '.~2')
        a('jungle', 'Cornelius')
        a('jungle', 'Pompadour')
        hg('commit', '-m', 'Counselor')
        pre1 = self.get_id('-3')
        pre2 = self.get_id('-2')
        succ = self.get_id('-1')
        hg('debugobsolete', pre1, succ)
        hg('debugobsolete', pre2, succ)
        self.refresh()
        # patch1 is folded (into patch2)
        patch1.cw_clear_all_caches()
        patch2.cw_clear_all_caches()
        succ = self.all_revs()[-1]
        assert succ.description == 'Counselor'
        self.assertTrue(succ.reverse_patch_revision)
        patch = succ.reverse_patch_revision[0]
        self.assertEqual(patch1.eid, patch.eid)
        self.assertEqual(2, len(patch1.patch_revision))
        self.assertEqual(1, len(patch2.patch_revision))
        patch1_state = patch1.cw_adapt_to('IWorkflowable').state
        self.assertEqual('pending-review', patch1_state)
        wf1_history = self.get_wf_history(patch1)
        self.assertEqual(['pending-review'], wf1_history)
        patch2_state = patch2.cw_adapt_to('IWorkflowable').state
        self.assertEqual('folded', patch2_state)
        wf2_history = self.get_wf_history(patch2)
        self.assertEqual(['pending-review', 'folded'], wf2_history)

class PatchNotificationTC(CubicWebTC):

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

    # XXX presetup
    def setup_database(self):
        req = self.request()
        # exist in the Mercurial repo
        self.create_user(req, 'Babar', ('users', 'reviewers', 'committers'),
                         email=u'babar@jungle.net')
        self.create_user(req, 'Victor', ('users', 'reviewers'),
                         email=u'victor@ratax.es')
        # unknown to the Mercurial repo
        self.create_user(req, 'Basile', ('users', 'reviewers'),
                         email=u'basile@ratax.es')
        self.commit()
        req.create_entity('Repository',
                          title=u'Jungle',
                          type=u'mercurial',
                          encoding=u'utf-8',
                          has_review=True,
                          path=self.full_repo_path)
        self.commit()
        init_vcsrepo(self.repo)

    def assertEmailEqual(self, email, subject, recipient, content):
        self.assertEqual(email.subject, subject)
        self.assertEqual(email.recipients, [recipient])
        expected = content.splitlines()
        got = email.content.splitlines()
        # we should print a diff like -/+ stuff
        for idx, line in enumerate(expected):
            self.assertMatches(line, got[idx])
        self.assertEqual(len(expected), len(got))

    def assertMatches(self, expected, got):
        """ expected is a regular expression """
        self.assertTrue(re.match(expected, got),
                        '%r\n does not match:\n %r' % (got, expected))


    def test_nosy_list_author(self):
        """Test that author of a patch is automatically added to the nosylist"""
        session = self.session
        victor = session.execute('Any X WHERE X login "Victor"').get_entity(0, 0)
        all_nosy = set(e.eid for e in victor.reverse_nosy_list)
        rset = session.execute('Any P WHERE P patch_revision R, '
                               '            R author ILIKE "Victor%"')
        victor_patch = set(eid for eid, in rset)
        self.assertTrue(victor_patch.issubset(all_nosy))
        patch = rset.get_entity(0, 0)
        self.assertEqual(victor.eid, patch.creator.eid)
        self.assertEqual(victor.name(), patch.dc_authors())

    def test_reviewer_email(self):
        session = self.session
        rql = 'Any R ORDERBY R DESC WHERE R is Revision'
        rev = session.execute(rql).get_entity(0, 0)
        assert rev.description == 'Add more elephants children'
        patch = rev.reverse_patch_revision[0]
        assert patch.patch_name == 'Add more elephants children'
        self.assertEqual(1, len(patch.patch_reviewer))
        reviewer = patch.patch_reviewer[0]
        self.assertIn(reviewer.login, ('Babar', 'Basile'))
        nosyed = set(u.login for u in patch.nosy_list)
        self.assertEqual(2, len(nosyed))
        self.assertIn(reviewer.login, nosyed)

        assert not MAILBOX # dunno why this is empty but it is
        patch.cw_adapt_to('IWorkflowable').fire_transition('ask rework',
                                                           u'coin coin')
        session.commit(free_cnxset=False)
        self.assertEqual(2, len(MAILBOX))
        MAILBOX[:] = []
        # patch are only send on ask review, so we reask for review
        patch.cw_adapt_to('IWorkflowable').fire_transition('ask review',
                                                           u'coin coin')
        session.commit(free_cnxset=False)
        self.assertEqual(2, len(MAILBOX))
        MAILBOX.sort(key=lambda e: 'victor@ratax.es' in e.recipients)
        review_email = MAILBOX[0]
        self.assertEmailEqual(review_email,
                              '[Jungle] patch pending-review: Add more elephants children',
                              [e.address for e in reviewer.primary_email][0],
                              '\n'
                              'admin changed status from <in-progress> to <pending-review> for entity\n'
                              "'Add more elephants children'\n"
                              '\n'
                              'coin coin\n'
                              '\n'
                              '\(No recorded task\)\n'
                              '\n'
                              'url: http://testing.fr/cubicweb/patch/\d+\n'
                              '\n'
                              '\n'
                              '# HG changeset patch\n'
                              '# User Victor <victor@ratax.es>\n'
                              '# Date 1361805588 0\n'
                              '# Node ID bfa5da61c82507b76dae7927b4fce2aa4a0c9c6f\n'
                              '# Parent  549cd3165597cdd5c9d8fa26e83e63483fcfb4b5\n'
                              'Add more elephants children\n'
                              '\n'
                              'diff --git a/babar.py b/babar.py\n'
                              '--- a/babar.py\n'
                              '\+\+\+ b/babar.py\n'
                              '@@ -5,10 \+5,15 @@\n'
                              " elephants = \['Babar',\n"
                              "              'Celeste',\n"
                              "              'Cornelius',\n"
                              "              'Pompadour',\n"
                              "              'Poutifour',\n"
                              "\+             'Arthur'\n"
                              "\+             'Pom',\n"
                              "\+             'Flore',\n"
                              "\+             'Alexandre',\n"
                              "\+             'Isabelle',\n"
                              '              \]\n'
                              ' \n'
                              ' \n'
                              " if __name__ == '__main__':\n"
                              "     print 'Those are elephants:'\n"
                              '\n')
        # add task
        MAILBOX[:] = ()
        task = session.create_entity('Task', title=u'todo', reverse_has_activity=patch)
        point = session.create_entity('InsertionPoint', lid=0, point_of=rev)
        session.create_entity('Task', title=u'my point', reverse_has_activity=point)
        session.commit(free_cnxset=False)
        self.assertEqual(4, len(MAILBOX))
        # reask review
        MAILBOX[:] = ()
        patch.cw_adapt_to('IWorkflowable').fire_transition('ask rework',
                                                           u'tasked')
        session.commit(free_cnxset=False)
        self.assertEqual(2, len(MAILBOX))
        MAILBOX.sort(key=lambda e: 'victor@ratax.es' in e.recipients)
        review_email = MAILBOX[0]
        self.assertEmailEqual(review_email,
                              '[Jungle] patch in-progress: Add more elephants children',
                              [e.address for e in reviewer.primary_email][0],
                              '\n'
                              'admin changed status from <pending-review> to <in-progress> for entity\n'
                              "'Add more elephants children'\n"
                              '\n'
                              'tasked\n'
                              '\n'
                              'remaining tasks:\n'
                              '\n'
                              '- my point\n'
                              '- todo\n'
                              '\n'
                              'url: http://testing.fr/cubicweb/patch/\d+\n'
                              '\n'
                              '\n'
                              '\n')

        # Test that comments are emailed too
        MAILBOX[:] = ()
        point.cw_clear_all_caches()
        comment = session.create_entity('Comment', comments=task,
                                        content=u'Babar comments')
        session.commit(free_cnxset=False)
        MAILBOX.sort(key=lambda e: 'victor@ratax.es' in e.recipients)
        self.assertEqual(2, len(MAILBOX))
        review_email = MAILBOX[0]
        self.assertEmailEqual(review_email,
                              'new comment for Task todo',
                              [e.address for e in reviewer.primary_email][0],
                              'Babar comments\n'
                              '\n\n'
                              'i18n_by_author_field: admin\n'
                              'url: http://testing.fr/cubicweb/task/%i' % task.eid)


PatchNotificationTC.repo_path = osp.join(PatchNotificationTC.datadir,
                                         u'demo-repo-final')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

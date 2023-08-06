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

import os.path as osp
from itertools import count, izip
from subprocess import CalledProcessError

from logilab.common.testlib import TestCase, unittest_main
from cubes.vcreview import compare_patches

from unittest_hooks import HgHelper

initialpatch="""# HG changeset patch
# User Victor <victor@ratax.es>
# Date 1362585681 -3600
# Node ID 70c874b4e12b01fc2a51c2dfdebc5c61b5da467c
# Parent  fbb870448944fadbdb30104109541a3316438717
[pkg] prepare release 1.0.0

pkginfo was already changed.

diff --git a/debian/changelog b/debian/changelog
--- a/debian/changelog
+++ b/debian/changelog
@@ -1,3 +1,10 @@
+cubicweb-vcreview (1.0.0-1) unstable; urgency=low
+
+  * new upstream release
+  * drop MQ backend in favor of changeset evolution
+
+ -- Pierre-Yves David <pierre-yves.david@logilab.fr>  Wed, 06 Mar 2013 16:59:11 +0100
+
 cubicweb-vcreview (0.10.1-1) unstable; urgency=low
 
   * new upstream release
diff --git a/debian/control b/debian/control
--- a/debian/control
+++ b/debian/control
@@ -2,14 +2,14 @@ Source: cubicweb-vcreview
 Section: web
 Priority: optional
 Maintainer: LOGILAB S.A. (Paris, FRANCE) <contact@logilab.fr>
-Build-Depends: debhelper (>= 5.0.37.1), python (>=2.4), python-dev (>=2.4)
+Build-Depends: debhelper (>= 5.0.37.1), python (>=2.6)
 Standards-Version: 3.8.0
 
 
 Package: cubicweb-vcreview
 Architecture: all
-Depends: cubicweb-common (>= 3.14.0),
-  cubicweb-vcsfile (>= 1.7.1), cubicweb-comment (>= 1.8.0),
+Depends: cubicweb-common (>= 3.15.8),
+  cubicweb-vcsfile (>= 1.12.0), cubicweb-comment (>= 1.8.0),
   cubicweb-task, cubicweb-nosylist
 Breaks: cubicweb-trackervcs (<< 1)
 Description: patch review system on top of vcsfile
"""

otherpatch="""# HG changeset patch
# User Victor <victor@ratax.es>
# Date 1362588960 -3600
# Node ID 3e6dbe86678c30c2a77a01da65f2842de287cb54
# Parent  46b2b7ffaf2096953433ba393c20c645eb11ddcd
Added tag cubicweb-vcreview-version-1.0.0 for changeset 46b2b7ffaf20

diff --git a/.hgtags b/.hgtags
--- a/.hgtags
+++ b/.hgtags
@@ -40,3 +40,4 @@ 2066c270a15bf59b7b6294353bb4e7c47e12df77
 3bd0fd59996885104d7a9435a8f665e79f4bac88 cubicweb-vcreview-debian-version-0.10.0-1
 f49629dd7ea14a93269b35d94b600401a885b30f cubicweb-vcreview-version-0.10.1
 e7005fcce2cdebc4875d147daad2d121f5e86146 cubicweb-vcreview-debian-version-0.10.1-1
+46b2b7ffaf2096953433ba393c20c645eb11ddcd cubicweb-vcreview-version-1.0.0
"""


class ComparePatch(TestCase):
    def assertSamePatch(self, old, new):
        self.assertTrue(compare_patches(old, new))

    def assertDiffPatch(self, old, new):
        self.assertFalse(compare_patches(old, new))

    def test_identity(self):
        self.assertSamePatch(initialpatch, initialpatch)

    def test_unrelated(self):
        self.assertDiffPatch(initialpatch, otherpatch)

    def test_user_change(self):
        victor = '# User Victor <victor@ratax.es>'
        assert victor in initialpatch
        podular = '# User Podular <podular@elephan.tz>'
        changed = initialpatch.replace(victor, podular)
        self.assertDiffPatch(initialpatch, changed)

    def test_node_change(self):
        ihash = '70c874b4e12b01fc2a51c2dfdebc5c61b5da467c'
        assert ihash in initialpatch
        nhash = 'kjcndsalkjncds'
        changed = initialpatch.replace(ihash, nhash)
        self.assertSamePatch(initialpatch, changed)

    def test_desc_change(self):
        idesc = 'pkginfo was already changed.'
        assert idesc in initialpatch
        ndesc = 'nothing'
        changed = initialpatch.replace(idesc, ndesc)
        self.assertDiffPatch(initialpatch, changed)

    def test_add_hunk(self):
        changed = initialpatch + otherpatch.split('\n\n')[1]
        self.assertDiffPatch(initialpatch, changed)

    def test_filename_change(self):
        ifn = 'debian/changelog'
        assert ifn in initialpatch
        changed = initialpatch.replace(ifn, 'debian/rules')
        self.assertDiffPatch(initialpatch, changed)

    def test_context_change(self):
        iprio = 'Priority: optional'
        assert iprio in initialpatch
        changed = initialpatch.replace(iprio, 'Priority: useless')
        self.assertDiffPatch(initialpatch, changed)

    def test_minus_change(self):
        iminus = '-Depends: cubicweb-common (>= 3.14.0),'
        assert iminus in initialpatch
        changed = initialpatch.replace(iminus,
                                       '-Depends: cubicweb-common (>= 3.14.1),')
        self.assertDiffPatch(initialpatch, changed)

    def test_plus_change(self):
        iplus = '+  * new upstream release'
        assert iplus in initialpatch
        changed = initialpatch.replace(iplus, '+  * bing')
        self.assertDiffPatch(initialpatch, changed)

class DetectRebaseTC(HgHelper):

    verbose_hg = False

    def setup_simple_repo(self):
        hg = self.call_hg
        a = self.append_to

        # create a root changeset
        a('jungle', 'Babar')
        hg('add', osp.join(self.tmprepo, 'jungle'))
        hg('commit', '-m', 'Initial jungle content')
        # with two children
        a('jungle', 'Celestine')
        hg('commit', '-m', 'Added Celestine')
        hg('up', '.^')
        a('village', 'Isabelle')
        hg('add', osp.join(self.tmprepo, 'village'))
        hg('commit', '-m', 'Added Isabelle in the village')
        # update to the first created child
        hg('up', 'desc(Celestine)')
        self.refresh()

    def setup_complex_repo(self):
        """build the following repo

        @ Pom is back in town
        |
        o Isabelle in the village
        |
        o Celeste in the jungle
        |
        o Babar in the jungle
        """
        hg = self.call_hg
        a = self.append_to

        def addcs(fn, content, msg):
            a(fn, content)
            hg('add', osp.join(self.tmprepo, fn))
            hg('commit', '-m', msg)

        addcs('jungle', 'Babar', 'Babar in the jungle')
        addcs('jungle', 'Celeste', 'Celeste in the jungle')
        addcs('village', 'Isabelle', 'Isabelle in the village')
        addcs('town', 'Pom', 'Pom is back in town')

        self.cs = dict(izip(('babar', 'celeste', 'isabelle', 'pom'), count(0)))

        self.refresh()


    def amend(self, rev, date, msg=None):
        hg = self.call_hg
        hg('up', str(rev))
        if msg is None:
            msg = self.all_revs()[rev].description
        hg('commit', '--amend', '-d', date, '-m', msg)
        try:
            hg('--config', 'extensions.rebase=', 'rebase',
               '--dest', '.', '--rev', 'unstable()')
        except CalledProcessError as exc:
            if exc.returncode != 1:
                raise
            # else, nothing to rebase


    def accept_patch(self, rev):
        """set patch associated with rev in reviewed state"""
        # get first child (rev #1)
        old = self.all_revs()[rev]
        patch = old.reverse_patch_revision[0]
        iwf = patch.cw_adapt_to('IWorkflowable')
        # ensure it's in pending-review state
        self.assertEqual('pending-review', iwf.state)
        # transition to accept
        iwf.fire_transition('accept')
        patch.cw_clear_all_caches()
        iwf = patch.cw_adapt_to('IWorkflowable')
        # ensure it is now reviewed
        self.assertEqual('reviewed', iwf.state)
        self.session.commit(free_cnxset=False)
        return patch

    def check_patch(self, patch, nrev, state):
        patch.cw_clear_all_caches()
        self.assertEqual(nrev, len(patch.patch_revision),
                         msg='Wrong number of revisions for %s' % patch.dc_title())
        iwf = patch.cw_adapt_to('IWorkflowable')
        self.assertEqual(state, iwf.state,
                         msg='Wrong state for %s' % patch.dc_title())

    def test_detect_amend(self):
        self.setup_simple_repo()
        # get first child (rev #1)
        patch = self.accept_patch(1)
        # rebase the first children on top of the second, this should trigger
        # the hook and patch comparison
        self.amend('.', '2008-06-30', 'Added Celestine')
        self.session.set_cnxset()
        self.refresh()
        # as it is a trivial change, patches are the same, hence the state is
        # is still reviewed
        self.check_patch(patch, 2, 'reviewed')

    def test_detect_rebase(self):
        self.setup_simple_repo()
        # get first child (rev #1)
        patch = self.accept_patch(1)
        # rebase the first children on top of the second, this should trigger
        # the hook and patch comparison
        self.call_hg('--config', 'extensions.rebase=', 'rebase')
        self.session.set_cnxset()
        self.refresh()
        # as it is a trivial rebase, patches are the same, hence the state is
        # is still reviewed
        self.check_patch(patch, 2, 'reviewed')

    def test_detect_rebase_and_amend(self):
        self.setup_complex_repo()
        hg = self.call_hg

        isabelle_patch = self.accept_patch(self.cs['isabelle'])
        babar_patch = self.accept_patch(self.cs['babar'])
        pom_patch = self.accept_patch(self.cs['pom'])
        celeste_patch = self.accept_patch(self.cs['celeste'])


        # change things
        self.amend(self.cs['isabelle'], '2000-01-01') # identical
        self.amend(self.cs['celeste'], '2001-09-11', 'plouf') # changed
        # strip intermediate ancestor of Pom
        hg('--config', 'extensions.mq=', 'strip',
           'desc(Pom) and obsolete() and 4:', '--hidden')

        self.session.set_cnxset()
        self.refresh()

        self.check_patch(babar_patch, nrev=1, state='reviewed')
        self.check_patch(pom_patch, nrev=2, state='reviewed')
        self.check_patch(isabelle_patch, nrev=3, state='reviewed')
        self.check_patch(celeste_patch, nrev=2, state='pending-review')

    def test_amend_then_rebase(self):
        self.setup_complex_repo()

        isabelle_patch = self.accept_patch(self.cs['isabelle'])

        self.amend(self.cs['isabelle'], '2001-09-11', 'PLAFF') # changed
        self.amend('tip^', '2001-09-12', 'PLAFF') # unchanged

        self.session.set_cnxset()
        self.refresh()

        self.check_patch(isabelle_patch, nrev=3, state='pending-review')


if __name__ == '__main__':
    unittest_main()

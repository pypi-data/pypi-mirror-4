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

from __future__ import with_statement

from cubicweb.selectors import traced_selection
from cubicweb.devtools.testlib import CubicWebTC

from cubes.comment.views import CommentSectionVComponent
from cubes.vcreview.views.components import ActivityComponent

class InsertPointTC(CubicWebTC):
    def test_ip_creation_comment_component(self):
        req = self.request()
        req.form['tempEid'] ='A'
        ipoint = req.vreg['etypes'].etype_class('InsertionPoint')(req)
        ipoint.eid = 'A'
        comps = list(req.vreg['ctxcomponents'].poss_visible_objects(
            req, rset=None, entity=ipoint, extra='pouet',
            context='navcontentbottom'))
        self.assertEqual(len(comps), 2)
        comp = comps[0]
        self.assertIsInstance(comp, ActivityComponent)
        comp = comps[1]
        self.assertIsInstance(comp, CommentSectionVComponent)
        l = []
        comp.render(l.append)
        self.assertTrue(''.join(l).startswith('<div class="section commentsection" id="commentsectionA">'))

    def test_ip_creation_comment_form(self):
        req = self.request()
        req.form['etype'] ='InsertionPoint'
        req.form['id'] ='1234'
        req.form['point_of'] ='5678'
        req.form['tempEid'] ='A'
        #with traced_selection():
        form = req.vreg['views'].select('addcommentform', req, etype='InsertionPoint')
        formstr = form.render()
        # XXX use page api
        pi = self.assertWellFormed(self.get_validator(), formstr)
        self.assertTrue(formstr.startswith('<div id="commentASlot"><form '))
        self.assertTrue(pi.has_tag('input', name="lid-subject:A", type="hidden"))
        self.assertTrue(pi.has_tag('input', name="point_of-subject:A", type="hidden"))
        self.assertTrue(pi.has_tag('textarea', cols="80", id="content-subject:A"))

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

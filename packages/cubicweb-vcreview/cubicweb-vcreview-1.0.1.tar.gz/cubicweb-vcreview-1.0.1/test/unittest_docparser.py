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

from logilab.common.testlib import TestCase, unittest_main, mock_object
from logilab.mtconverter import TransformData

from cubicweb import devtools
from cubicweb.mttransforms import ENGINE

from cubes.vcsfile.docparser import Diff2HTMLTransform

class FakeRequest(object):
    def add_css(self, file): pass

class DiffParserTC(TestCase):
    @classmethod
    def setUpClass(cls):
        # in case a previous test set this up
        try:
            ENGINE.remove_transform(Diff2HTMLTransform.name)
        except KeyError:
            pass

    def transform(self, file):
        data = open(self.datapath(file)).read()
        trdata = TransformData(data, 'text/x-diff', 'utf-8')
        trdata.appobject = mock_object(_cw=FakeRequest())
        return ENGINE.convert(trdata, 'text/annotated-html').data

    def setUp(self):
        def insert_point_cb(ipid, trdata, w):
            w('<hr class="%s"/>' % ipid)
            self.ipid = ipid
        ENGINE.add_transform(Diff2HTMLTransform(insert_point_cb))

    def tearDown(self):
        ENGINE.remove_transform(Diff2HTMLTransform.name)

    def test_insert_point_1(self):
        htmldata = self.transform('pytestgc.diff')
        self.assertEqual(self.ipid, 5)
        self.assertTrue(htmldata.startswith('<div class="text/x-diff">'))

    def test_insert_point_2(self):
        htmldata = self.transform('nonregr1.diff')
        self.assertEqual(self.ipid, 2)
        self.assertTrue(htmldata.startswith('<div class="text/x-diff">'))

    def test_insert_point_3(self):
        htmldata = self.transform('nonregr2.diff')
        self.assertEqual(self.ipid, 3)
        self.assertTrue(htmldata.startswith('<div class="text/x-diff">'))

if __name__ == '__main__':
    unittest_main()

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
"""cubicweb-vcreview web ui"""

__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.web import uicfg, formwidgets as wdg

_affk = uicfg.autoform_field_kwargs
_abaa = uicfg.actionbox_appearsin_addmenu
_pvs = uicfg.primaryview_section

# insertion point handling #####################################################

_pvs.tag_object_of(('InsertionPoint', 'point_of', '*'), 'hidden')
_abaa.tag_object_of(('InsertionPoint', 'point_of', '*'), False)
_abaa.tag_subject_of(('InsertionPoint', 'has_activity', '*'), False)
_affk.tag_attribute(('InsertionPoint', 'lid'),
                    {'widget': wdg.HiddenInput})
_affk.tag_subject_of(('InsertionPoint', 'point_of', '*'),
                     {'widget': wdg.HiddenInput})


# utility functions ############################################################

def patch_states_rql(req):
    states = req.vreg['etypes'].etype_class('Patch').non_final_states
    return 'IN (%s)' % ','.join(repr(s) for s in states)

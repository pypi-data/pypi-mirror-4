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
"""cubicweb-vcreview custom forms"""

__docformat__ = "restructuredtext en"

from datetime import datetime

from cubicweb.selectors import (is_instance, rql_condition, attribute_edited,
                                match_transition, match_user_groups)
from cubicweb.uilib import cut
from cubicweb.web import uicfg, formfields
from cubicweb.web.views import workflow, editviews, autoform

_affk = uicfg.autoform_field_kwargs



class AskReviewPatchChangeStateForm(workflow.ChangeStateForm):
    __select__ = is_instance('Patch') & (
        match_user_groups('managers', 'committers')
        | rql_condition('X patch_revision RE, RE from_repository R, R repository_committer U')
        ) & (
        match_transition('ask review')
        | attribute_edited('patch_reviewer'))

    patch_reviewer = autoform.etype_relation_field('Patch', 'patch_reviewer', 'subject')



class RevisionComboboxView(editviews.ComboboxView):
    __select__ = is_instance('Revision')
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w('%s: %s' % (
            entity.dc_title(),
            cut(entity.description,
                self._cw.property_value('navigation.short-line-size'))))


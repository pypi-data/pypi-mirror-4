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
"""cubicweb-vcreview facets to filter patches"""

__docformat__ = "restructuredtext en"

from cubicweb.web import facet
from cubicweb.selectors import is_instance

class PatchRepositoryFacet(facet.RQLPathFacet):
    __regid__ = 'vcreview.patch_repository'
    __select__ = is_instance('Patch')
    path = ['X patch_revision RE', 'RE from_repository R', 'R title T']
    title = 'Repository'
    filter_variable = 'R'
    label_variable = 'T'


class PatchReviewerFacet(facet.RelationFacet):
    __regid__ = 'vcreview.patch_reviewer'
    rtype = 'patch_reviewer'
    role = 'subject'
    target_attr = 'login'


class PatchAuthorFacet(facet.RQLPathFacet):
    __regid__ = 'vcreview.patch_author'
    __select__ = is_instance('Patch')
    title = 'Author'
    path = ['X patch_revision RE', 'RE author A']
    filter_variable = 'A'

class PatchBranchFacet(facet.RQLPathFacet):
    __regid__ = 'vcreview.patch_branch'
    __select__ = is_instance('Patch')
    title = 'Branch'
    path = ['X patch_revision RE', 'RE branch B']
    filter_variable = 'B'

class PatchCommitterFacet(facet.RelationFacet):
    __regid__ = 'vcreview.patch_committer'
    rtype = 'patch_committer'
    role = 'subject'
    target_attr = 'login'

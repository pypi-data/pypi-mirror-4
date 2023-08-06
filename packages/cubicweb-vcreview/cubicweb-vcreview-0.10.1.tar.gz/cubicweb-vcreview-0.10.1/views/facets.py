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


class PatchRepositoryFacet(facet.RelationFacet):
    __regid__ = 'vcreview.patch_repository'
    rtype = 'patch_repository'
    role = 'subject'
    label_vid = 'text'


class PatchReviewerFacet(facet.RelationFacet):
    __regid__ = 'vcreview.patch_reviewer'
    rtype = 'patch_reviewer'
    role = 'subject'
    target_attr = 'login'


class PatchOriginatorFacet(facet.AttributeFacet):
    __regid__ = 'vcreview.patch.originator'
    __select__ = facet.AttributeFacet.__select__ & is_instance('Patch')
    rtype = 'originator'
    i18nable = False


class PatchBranchFacet(facet.AttributeFacet):
    __regid__ = 'vcvreview.patch.branch'
    __select__ = facet.AttributeFacet.__select__ & is_instance('Patch')
    rtype = 'branch'
    i18nable = False

class PatchCommitterFacet(facet.RelationFacet):
    __regid__ = 'vcreview.patch_committer'
    rtype = 'patch_committer'
    role = 'subject'
    target_attr = 'login'

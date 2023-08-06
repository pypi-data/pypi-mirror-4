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
"""cubicweb-vcreview primary views and adapters for the web ui"""

__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb import tags
from cubicweb.selectors import score_entity, is_instance
from cubicweb.view import EntityView
from cubicweb.schema import display_name
from cubicweb.web import uicfg
from cubicweb.web.views import tabs, primary, ibreadcrumbs

from cubes.vcsfile.views import primary as vcsfile
from cubes.vcreview.views import final_patch_states_rql
from cubes.vcreview.site_cubicweb import COMPONENT_CONTEXT

_pvs = uicfg.primaryview_section
_pvdc = uicfg.primaryview_display_ctrl
_abaa = uicfg.actionbox_appearsin_addmenu
_afs = uicfg.autoform_section


# patch primary view ###########################################################

_pvs.tag_subject_of(('Patch', 'patch_reviewer', '*'), 'attributes')
_pvs.tag_subject_of(('Patch', 'patch_committer', '*'), 'attributes')
_pvdc.tag_subject_of(('Patch', 'applied_at', '*'), {'vid': 'incontext'})

class PatchPrimaryView(tabs.TabbedPrimaryView):
    """Main Patch primary view"""
    __select__ = is_instance('Patch')

    tabs = [_('vcreview.patch.tab_main'),
            _('vcreview.patch.tab_head')]
    default_tab = 'vcreview.patch.tab_main'

    def render_entity_title(self, entity):
        self.w(u'<h1>%s <span class="state">[%s]</span></h1>'
               % (xml_escape(entity.dc_title()),
                  xml_escape(entity.cw_adapt_to('IWorkflowable').printable_state)))


class PatchPrimaryTab(tabs.PrimaryTab):
    """Summary tab for Patch"""
    __regid__ = 'vcreview.patch.tab_main'
    __select__ = is_instance('Patch')

    def render_entity_attributes(self, entity):
        super(PatchPrimaryTab, self).render_entity_attributes(entity)
        self.w(u'<h4>%s</h4>' % self._cw._('Patch revisions'))
        rset = self._cw.execute(
            'Any R,RA,RB,RC,RD,R ORDERBY RC DESC '
            'WHERE X eid %(x)s, X patch_revision R,'
            'R author RA, R branch RB, R creation_date RC, R description RD',
            {'x': entity.eid})
        _, __ = self._cw._, self._cw.__
        self.wview('table', rset,
                   headers=[__('Revision'), __('author'), __('branch'),
                            __('creation_date'), __('commit message')])

class PatchHeadTab(EntityView):
    """Revision view of the tip most version of the patch

    (with comment and task)"""
    __regid__ = 'vcreview.patch.tab_head'
    __select__ = is_instance('Patch')

    def entity_call(self, entity):
        tip = entity.tip()
        if tip:
            tip.view('primary', w=self.w)


#_pvs.tag_object_of(('*', 'patch_revision', '*'), 'hidden') # in breadcrumbs

# repository primary view ######################################################

_pvs.tag_subject_of(('Repository', 'repository_committer', '*'), 'attributes')
_pvs.tag_subject_of(('Repository', 'repository_reviewer', '*'), 'attributes')


class RepositoryPatchesTab(EntityView):
    __regid__ = _('vcreview.patches_tab')
    __select__ = is_instance('Repository') & score_entity(lambda x: x.has_review)

    def entity_call(self, entity):
        entity.view('vcreview.repository.patches', w=self.w)

vcsfile.RepositoryPrimaryView.tabs.append(RepositoryPatchesTab.__regid__)


class RepositoryPatchesTable(EntityView):
    __regid__ = 'vcreview.repository.patches'
    __select__ = is_instance('Repository') & score_entity(lambda x: x.has_review)

    rql = ('Any P,PO,P,P,PB,PS,COUNT(TR) ' # XXX need a sub query to find patch tip
           'GROUPBY P,PO,PB,PS '
           'WHERE '
           '      RE branch PB, '
           '      P in_state PS, '
           '      TR? wf_info_for P, '
           '      P patch_revision RE, '
           '      RE from_repository R, '
           '      RE author PO, '
           '      R eid %(x)s')

    def entity_call(self, entity):
        linktitle = self._cw._('Patches for %s') % entity.dc_title()
        linkurl = self._cw.build_url(rql=self.rql % {'x': entity.eid},
                                     vtitle=linktitle)
        self.w('<p>%s. <a href="%s">%s</a></p>' % (
            self._cw._('Table below only show active patches'),
            xml_escape(linkurl), self._cw._('Show all patches')))
        rql = self.rql + ', NOT PS name %s' % final_patch_states_rql(self._cw)
        rset = self._cw.execute(rql, {'x': entity.eid})
        self.wview('vcreview.patches.table', rset, 'noresult', displayfilter=True)

# task primary view ############################################################

_pvs.tag_object_of(('*', 'has_activity', 'Task'), 'attributes')

class InsertionPointInContextView(EntityView):
    __regid__ = 'incontext'
    __select__ = is_instance('InsertionPoint')
    def entity_call(self, entity):
        purl = entity.parent.absolute_url()
        url = '%s#%s%s' % (purl, COMPONENT_CONTEXT, entity.eid)
        self.w(u'<a href="%s">%s</a>' % (url, entity.parent.dc_title()))


# breadcrumbs ##################################################################

class PatchIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('Patch')

    def parent_entity(self):
        return self.entity.repository

class TaskBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = (is_instance('Task')
                  & score_entity(lambda x: x.reverse_has_activity))

    def parent_entity(self):
        return self.entity.reverse_has_activity[0]


class InsertionPointBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('InsertionPoint')

    def parent_entity(self):
        return self.entity.parent

    def breadcrumbs(self, view=None, recurs=None):
        path = super(InsertionPointBreadCrumbsAdapter, self).breadcrumbs(
            view, recurs)
        return [x for x in path if getattr(x, 'eid', None) != self.entity.eid]

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
"""cubicweb-vcreview components (boxes, pluggable sections)"""

__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb.selectors import (is_instance, relation_possible,
                                score_entity, match_form_params)
from cubicweb import tags, uilib, view
from cubicweb.web import uicfg, component, form, formwidgets as wdg
from cubicweb.view import EntityView
from cubicweb.web.views import (workflow, idownloadable, ajaxedit,
                                forms, formrenderers)

from cubes.comment import views as comment
from cubes.vcreview.site_cubicweb import COMPONENT_CONTEXT

_afs = uicfg.autoform_section
_affk = uicfg.autoform_field_kwargs
_abaa = uicfg.actionbox_appearsin_addmenu
_pvs = uicfg.primaryview_section



# activities ###################################################################

_pvs.tag_subject_of(('*', 'has_activity', '*'), 'hidden') # component
_affk.tag_object_of(('*', 'has_activity', 'Task'),
                    {'widget': wdg.HiddenInput})


class AddActivityFormView(form.FormViewMixIn, view.EntityView):
    __regid__ = 'vcreview.addactivityform'
    __select__ = (relation_possible('has_activity', 'subject', 'Task', 'add')
                  | match_form_params('etype'))

    def call(self, **kwargs):
        if self.cw_rset is None:
            entity = self._cw.vreg['etypes'].etype_class(self._cw.form['etype'])(self._cw)
            entity.eid = self._cw.form['tempEid']
            self.entity_call(entity)
        else:
            super(AddActivityFormView, self).call(**kwargs)

    def entity_call(self, container):
        self._cw.add_js(('cubicweb.edition.js', 'cubes.vcreview.js'))
        activity = self._cw.vreg['etypes'].etype_class('Task')(self._cw)
        activity.eid = self._cw.varmaker.next()
        okjs = uilib.js.addActivity(container.eid, not container.has_eid(),
                                    self.cw_extra_kwargs.get('context'))
        canceljs = "jQuery('#activity%sSlot').remove()" % container.eid
        form, formvalues = ajaxedit.ajax_composite_form(
            container, activity, 'has_activity', okjs, canceljs,
            dict(display_fields=(('title', 'subject'),
                                 ('description', 'subject'),
                                 ('has_activity', 'object'))))
        self.w(u'<div id="activity%sSlot">' % container.eid)
        form.render(w=self.w, main_form_title=u'', formvalues=formvalues)
        self.w(u'</div>')


class ActivityComponent(component.EntityCtxComponent):
    """a component to display an html section displaying activities related to
    an object
    """
    __regid__ = 'vcreview.activitysection'
    __select__ = (component.EntityCtxComponent.__select__
                  & relation_possible('has_activity', 'subject', 'Task'))

    context = 'navcontentbottom'

    def render_body(self, w):
        req = self._cw
        req.add_js('cubicweb.ajax.js')
        if self.entity.has_eid():
            self.display_existing_tasks(w)
            eid = self.entity.eid
        else:
            eid = None
        rdef = self.entity.e_schema.rdef('has_activity', 'subject', 'Task')
        if (req.vreg.schema['Task'].has_perm(req, 'add') and
            rdef.has_perm(req, 'add', fromeid=eid)):
            url = self.lazy_view_holder(w, self.entity, 'vcreview.addactivityform')
            w(u'(<a href="%s">%s</a>)' % (xml_escape(url), req._('add a task')))

    existing_tasks_rql = (
        u'Any T,TD,T,TCD,U, TS,TT,TDF,UL,UF,US ORDERBY TCD DESC WHERE '
        'X has_activity T, T description TD, T in_state TS,'
        'T creation_date TCD, T created_by U?,'
        'T title TT, T description_format TDF, '
        'U login UL, U firstname UF, U surname US, X eid %(x)s')

    def display_existing_tasks(self, w):
        rset = self._cw.execute(self.existing_tasks_rql, {'x': self.entity.eid})
        if rset:
            w(u'<h4>%s</h4>' % self._cw._('Activities'))
            self._cw.view('vcreview.task-view', rset, w=w)
class TaskView(EntityView):
    """a component to display an html section displaying activities related to
    an object
    """
    __regid__ = 'vcreview.task-view'
    __select__ = EntityView.__select__ & is_instance('Task')

    def cell_call(self, row, col):
        self._cw.add_css('cubes.vcreview.css')
        assert col == 0
        task = self.cw_rset.get_entity(row, col)
        iwf  = task.cw_adapt_to('IWorkflowable')
        assert iwf.state in ('todo', 'done'), iwf.state
        self.w(u'<div class="vcreview_task task_%s">' % iwf.state)
        self.w(u'<h5>')
        self.w(u'<span class="vcreview_taskstate">')
        self.w(iwf.printable_state)
        self.w(u'</span>')
        self.w(u'<span class="vcreview_tasktitle">')
        self.wview(u'vcreview.task-link', rset=self.cw_rset, row=row, col=col)
        self.w(u'</span>')
        if self._can_mark_as_done(iwf):
            url = self._mark_as_done_callback(task.eid)
            self.w(tags.input(type='button', onclick=url,
                              value='mark as done', klass="task_is_done"))
        self.w(u'</h5>')
        self.w(u'<p class="vcreview_taskinfo">Created ')
        self.w(task.printable_value('creation_date'))
        if task.created_by:
            self.w(u' by ')
            self.wview(u'incontext', rset=task.created_by[0].as_rset())
        self.w(u'</p>')
        self.w(u'<div id="vcreview_taskdescription">')
        self.w(task.view('reledit', rtype='description'))
        self.w(u'</div>')

        self.w(u'<div id="navcontentbottom%s">' % task.eid)
        comp = self._cw.vreg['ctxcomponents'].select_or_none('commentsection',
            self._cw,
            rset=task.as_rset(),
            entity=task,
            context='navcontentbottom',
            __cache=None)
        if comp is not None:
            comp.render(w=self.w)
        self.w(u'</div>')

        self.w(u'</div>')

    @staticmethod
    def _can_mark_as_done(iwf):
        if iwf.state != 'todo':
            return False
        for transition in iwf.possible_transitions():
            if transition.name == 'done':
                return True
        else:
            return False # task workflow changed or no permission to go through the transition

    def _mark_as_done_callback(self, eid):
        def change_state(req, eid):
            entity = req.entity_from_eid(eid)
            entity.cw_adapt_to('IWorkflowable').fire_transition('done')
        return self._cw.user_callback(change_state, (eid,))


class PatchActivityComponent(ActivityComponent):
    __select__ = ActivityComponent.__select__ & is_instance('Patch')
    existing_tasks_rql = (
        u'Any T,TD,T,TCD,U, TS,TT,TDF,UL,UF,US ORDERBY TCD DESC '
        'WITH T,TD,TS,TCD,U,TT,TDF,UL,UF,US BEING ('
        '(Any T,TD,TS,TCD,U,TT,TDF,UL,UF,US WHERE '
        'X has_activity T, T description TD, T in_state TS,'
        'T creation_date TCD, T created_by U?, '
        'T title TT, T description_format TDF, '
        'U login UL, U firstname UF, U surname US, X eid %(x)s)'
        ' UNION '
        '(Any T,TD,TS,TCD,U,TT,TDF,UL,UF,US WHERE '
        'X patch_revision RE, IP point_of RE, IP has_activity T, '
        'T description TD, T in_state TS, T creation_date TCD, '
        'T created_by U?, T title TT, T description_format TDF, '
        'U login UL, U firstname UF, U surname US, X eid %(x)s)'
        ')')


workflow.WFHistoryVComponent.order = 10
ActivityComponent.order = 20
comment.CommentSectionVComponent.order = 30




class TaskLinkView(form.FormViewMixIn, view.EntityView):
    __regid__ = 'vcreview.task-link'
    __select__ = is_instance('Task')
    def entity_call(self, entity):
        self.w(entity.view('incontext'))
        if entity.reverse_has_activity[0].__regid__ == 'InsertionPoint' \
               and self._cw.form.get('vid') == 'vcreview.patch.tab_main':
            ip = entity.reverse_has_activity[0]
            purl = ip.parent.absolute_url()
            url = u'%s#%s%s' % (purl, COMPONENT_CONTEXT, ip.eid)
            self.w(u' (<a href="%s">%s</a>)' % (url, self._cw._('see in context')))


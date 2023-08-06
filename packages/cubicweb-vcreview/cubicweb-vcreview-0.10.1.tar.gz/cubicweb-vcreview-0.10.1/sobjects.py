
from cubicweb.selectors import is_instance, is_in_state
from cubicweb.sobjects.notification import StatusChangeMixIn, NotificationView
from cubes.task import hooks as task

class PatchStatusChangeView(StatusChangeMixIn, NotificationView):
    __select__ = is_instance('Patch') & is_in_state('pending-review',
                                                    'in-progress',
                                                    'reviewed',
                                                    'applied',
                                                    'rejected')

    def subject(self):
        entity = self.cw_rset.get_entity(0, 0)
        return self._cw._(u'[%(repo)s] patch %(state)s: %(patch)s') % {
            'repo': entity.repository.dc_title(),
            'patch': entity.dc_title(),
            'state': self._cw.__(self._kwargs['current_state'])}

    def context(self, **kwargs):
        context = super(PatchStatusChangeView, self).context(**kwargs)
        entity = self.cw_rset.get_entity(0, 0)
        tasks = []
        for task in self._cw.execute(
            u'Any T,TT ORDERBY TCD DESC '
            'WHERE T in_state TS, TS name "todo" '
            'WITH T,TT,TCD BEING ('
            '(Any T,TT,TCD WHERE '
            'X has_activity T, T title TT, T creation_date TCD, X eid %(x)s)'
            ' UNION '
            '(Any T,TT,TCD WHERE '
            'X patch_revision VC, IP point_of VC, IP has_activity T, '
            'T title TT, T creation_date TCD, X eid %(x)s)'
            ')', {'x': entity.eid}).entities():
            tasks.append(task.dc_title())
        if tasks:
            context['comment'] += '\n\n%s\n\n- %s' % (
                self._cw._('remaining tasks:'), '\n- '.join(tasks))
        return context


class TaskAddedView(task.TaskAddedView):
    """get notified from new tasks"""
    __select__ = is_instance('Task')
    content_attr = 'description'

    def subject(self):
        entity = self.cw_rset.get_entity(0, 0)
        patch = entity.activity_of
        if not patch:
            return super(TaskAddedView, self).subject()
        if patch.__regid__ == 'InsertionPoint':
            patch = patch.parent.patch
            if not patch:
                return super(TaskAddedView, self).subject()
        return self._cw._(u'[%(repo)s] patch task: %(patch)s - %(task)s') % {
            'repo': patch.repository.dc_title(),
            'patch': patch.dc_title(),
            'task': entity.dc_title()}


class ReviewerSetNotificationView(NotificationView):
    __regid__ = 'vcreview.notifications.reviewer-set'
    __select__ = is_instance('Patch')
    content = _('''
You have been assigned for review of patch %(title)s

url: %(url)s
''')
    def recipients(self):
        reviewer = self.cw_extra_kwargs['user']
        email = reviewer.cw_adapt_to('IEmailable').get_email()
        if email:
            return [(email, reviewer.property_value('ui.language'))]
        return []

    def subject(self):
        patch = self.cw_rset.get_entity(0, 0)
        return self._cw._('[%(repo)s] patch assigned: %(patch)s') % {
            'app': self._cw.vreg.config.appid,
            'repo': patch.repository.dc_title(),
            'patch': patch.dc_title()}


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (TaskAddedView,))
    vreg.register_and_replace(TaskAddedView, task.TaskAddedView)

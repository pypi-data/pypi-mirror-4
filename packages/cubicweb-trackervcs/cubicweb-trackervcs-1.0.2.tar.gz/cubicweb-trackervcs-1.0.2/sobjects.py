def registration_callback(vreg):
    if 'vcreview' not in vreg.config.cubes():
        return

    from cubes.vcreview import sobjects as vcreview

    class PatchStatusChangeView(vcreview.PatchStatusChangeView):
        def subject(self):
            patch = self.cw_rset.get_entity(0, 0)
            if patch.repository.project:
                repo_title = patch.repository.project.dc_title()
            else:
                repo_title = patch.repository.dc_title()
            return self._cw.__(u'[%(repo)s] patch %(state)s: %(patch)s') % {
                'repo': repo_title,
                'patch': patch.dc_title(),
                'state': self._cw.__(self._kwargs['current_state'])}

    class TaskAddedView(vcreview.TaskAddedView):
        def subject(self):
            task = self.cw_rset.get_entity(0, 0)
            patch = task.activity_of
            if not patch:
                return super(TaskAddedView, self).subject()
            if patch.__regid__ == 'InsertionPoint':
                patch = patch.parent.patch
                if not patch:
                    return super(TaskAddedView, self).subject()
            if patch.repository.project:
                repo_title = patch.repository.project.dc_title()
            else:
                repo_title = patch.repository.dc_title()
            return self._cw.__(u'[%(repo)s] patch task: %(patch)s - %(task)s') % {
                'repo': repo_title,
                'patch': patch.dc_title(),
                'task': task.dc_title()}

    class ReviewerSetNotificationView(vcreview.ReviewerSetNotificationView):
        def subject(self):
            patch = self.cw_rset.get_entity(0, 0)
            if patch.repository.project:
                repo_title = patch.repository.project.dc_title()
            else:
                repo_title = patch.repository.dc_title()
            return self._cw.__('[%(repo)s] patch assigned: %(patch)s') % {
                'repo': repo_title,
                'patch': patch.dc_title()}

    vreg.register_and_replace(PatchStatusChangeView, vcreview.PatchStatusChangeView)
    vreg.register_and_replace(TaskAddedView, vcreview.TaskAddedView)
    vreg.register_and_replace(ReviewerSetNotificationView, vcreview.ReviewerSetNotificationView)

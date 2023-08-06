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
"""cubicweb-trackervcs views"""

from cubicweb.view import EntityView
from cubicweb.selectors import is_instance, score_entity, adaptable
from cubicweb.web import uicfg, facet
from cubicweb.web.views import ibreadcrumbs


# XXX in cw > 3.12.4 as 'incontext-state'
class InContextWithStateView(EntityView):
    __regid__ = 'myincontext-state'
    __select__ = adaptable('IWorkflowable')
    def entity_call(self, entity):
        iwf = entity.cw_adapt_to('IWorkflowable')
        self.w(u'%s [%s]' % (entity.view('incontext'), iwf.printable_state))


class TicketInContextWithStateAndVersionView(EntityView):
    __regid__ = 'incontext-state-version'
    __select__ = is_instance('Ticket')
    def entity_call(self, entity):
        state = entity.cw_adapt_to('IWorkflowable').printable_state
        if entity.done_in:
            self.w(u'%s [%s, %s]' % (entity.view('incontext'), state,
                                     entity.done_in[0].view('incontext')))
        else:
            self.w(u'%s [%s]' % (entity.view('incontext'), state))


class ProjectPatchesTab(EntityView):
    __regid__ = 'vcreview.patches_tab'
    __select__ = is_instance('Project') & score_entity(
        lambda x: x.source_repository and x.source_repository[0].has_review)

    def entity_call(self, entity):
        entity.source_repository[0].view(
            'vcreview.repository.patches', w=self.w)


class VersionPatchesTab(EntityView):
    __regid__ = 'trackervcs.version_patches_tab'
    __select__ = is_instance('Version') & score_entity(
        lambda x: x.project.source_repository and x.project.source_repository[0].has_review)

    def entity_call(self, entity):
        rql = ('Any P,PO,P,P,PB,PS,COUNT(TR) GROUPBY P,PO,PB,PS '
               'WHERE P patch_revision RE, RE author PO, RE branch PB, P in_state PS, '
               'TR? wf_info_for P, RE from_repository R, P patch_ticket T, '
               'T done_in V, V eid %(v)s')
        rset = self._cw.execute(rql, {'v': entity.eid})
        self.wview('vcreview.patches.table', rset, 'noresult')

class HasPatchFacet(facet.HasRelationFacet):
    __regid__ = 'trackervcs.has-patch-facet'
    rtype = 'patch_ticket'
    role = 'object'

class HasTicketFacet(facet.HasRelationFacet):
    __regid__ = 'trackervcs.has-ticket-facet'
    rtype = 'patch_ticket'
    role = 'subject'


def registration_callback(vreg):
    if not 'vcreview' in vreg.config.cubes():
        return # don't register anything from this module

    from cubicweb.web.views import tableview
    from cubes.vcreview.views import (startup as vcreview_startup,
                                      primary as vcreview_primary)
    from cubes.tracker.views import project, version

    vreg.register_all(globals().values(), __name__)

    # overridde vcreview summary tables to include patch's ticket and ticket's
    # version
    vcreview_startup.AllActivePatches.rql = (
        'Any P,PO,P,P,PB,PS,COUNT(TR),R,T,V GROUPBY R,P,PO,PB,PS,T,V '
        'ORDERBY RT,PB,PO WHERE P patch_revision RE, RE author PO, RE branch PB, P in_state PS, '
        'TR? wf_info_for P, RE from_repository R, R title RT, '
        'NOT PS name %s, '
        'P patch_ticket T?, T done_in V?')
    vcreview_startup.UserWorkList.rql = (
        'Any P,PO,P,P,PB,PS,COUNT(TR),R,T,V GROUPBY R,P,PO,PB,PS,T,V '
        'ORDERBY RT,PB,PO WHERE P patch_revision RE, RE author PO, RE branch PB, P in_state PS,'
        'TR? wf_info_for P, RE from_repository R, R title RT, U eid %(u)s, '
        'EXISTS(PS name "pending-review" AND P patch_reviewer U) '
        'OR EXISTS(PS name "reviewed" AND P patch_committer U) '
        'OR (EXISTS(PS name IN ("reviewed", "deleted") AND NOT EXISTS(P patch_committer U) '
        '    AND (EXISTS(R repository_committer U) OR EXISTS(U in_group G, G name "committers")))), '
        'P patch_ticket T?, T done_in V?')
    vcreview_primary.RepositoryPatchesTable.rql = (
        'Any P,PO,P,PB,PS,COUNT(TR),T,V GROUPBY P,PO,PB,PS,T,V WHERE '
        'P patch_revision RE, RE author PO, RE branch PB, P in_state PS, TR? wf_info_for P, '
        'RE from_repository R, R eid %(x)s, '
        'P patch_ticket T?, T done_in V?')
    # add a tab on project view to display patches
    project.ProjectPrimaryView.tabs.append(ProjectPatchesTab.__regid__)
    # uicfg tweaks
    _pvs = uicfg.primaryview_section
    _pvdc = uicfg.primaryview_display_ctrl
    _pvs.tag_subject_of(('Patch', 'patch_ticket', '*'), 'attributes')
    _pvdc.tag_subject_of(('Patch', 'patch_ticket', '*'), {'vid': 'incontext-state-version'})
    _pvs.tag_object_of(('*', 'patch_ticket', 'Ticket'), 'attributes')
    _pvdc.tag_object_of(('*', 'patch_ticket', 'Ticket'), {'vid': 'myincontext-state'})

    project.ProjectTicketsTable.columns.append('patch_ticket')
    project.ProjectTicketsTable.column_renderers['patch_ticket'] = \
        tableview.RelationColRenderer(role='object')
    version.VersionTicketsTable.columns.append('patch_ticket')
    version.VersionTicketsTable.column_renderers['patch_ticket'] = \
        tableview.RelationColRenderer(role='object')
    version.VersionPrimaryView.tabs.append(_('trackervcs.version_patches_tab'))


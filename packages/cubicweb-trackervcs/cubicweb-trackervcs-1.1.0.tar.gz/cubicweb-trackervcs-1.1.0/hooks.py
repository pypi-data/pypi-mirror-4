# copyright 2011-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-trackervcs specific hooks and operations"""

import re

from rql import TypeResolverException

from cubicweb import typed_eid
from cubicweb.server import hook
from cubicweb.selectors import is_instance

from cubes.tracker import hooks as tracker

_BASE_RE = r'\b%s\b\s+(#\d+(?:(?:,|\s|\s+and\s)\s*#\d+)*)'
CLOSES_EID_RGX = re.compile(_BASE_RE % 'closes', re.IGNORECASE)
RELATED_EID_RGX = re.compile(_BASE_RE % '(?:closes|related to)', re.IGNORECASE)
TICKET_EID_RGX = re.compile(r'#(\d+)')

def closed_eids(line):
    """Parse closes command in description and return target eids"""
    eids = []
    for cmd in CLOSES_EID_RGX.findall(line):
        eids.extend(int(m) for m in TICKET_EID_RGX.findall(cmd))
    return eids

def related_eids(line):
    """Parse closes and related commands in description and return target eids
    """
    eids = []
    for cmd in RELATED_EID_RGX.findall(line):
        eids.extend(int(m) for m in TICKET_EID_RGX.findall(cmd))
    return eids

def tickets(session, ticket_eids, repository_eid):
    """Return rset for a ticket referenced in a commit message.

    The ticket must come from a project using given repository as
    source_repository (or one of its subproject).

    Return None if no match.
    """
    for ticket_eid in ticket_eids:
        try:
            rset = session.execute('Any X, P WHERE X eid %(x)s, X concerns P',
                                   {'x': ticket_eid})
        except TypeResolverException: # ticket_eid is not a ticket
            continue
        if not rset: # ticket_eid doesn't exist
            continue
        project = rset.get_entity(0, 1)
        while project:
            if project.source_repository:
                if project.source_repository[0].eid == repository_eid:
                    yield rset.get_entity(0, 0)
                else:
                    break
            project = project.subproject_of and project.subproject_of[0]

# search for ticket closing instructions #######################################


_CLOSED_BY_RQL = '''
SET T closed_by R
WHERE NOT T closed_by R,
      T eid %(t)s,
      R eid %(r)s
'''
class SearchRevisionTicketOp(hook.DataOperationMixIn,
                             hook.Operation):
    """Search magic words in revision's commit message:

        closes #<ticket eid>

    When found, the ticket is marked as closed by the revision and its state is
    changed.
    """
    def precommit_event(self):
        for rev_eid in self.get_data():
            # search for instruction
            rev = self.session.entity_from_eid(rev_eid)
            eids = closed_eids(rev.description)
            for ticket in tickets(self.session, eids, rev.repository.eid):
                if rev.phase == 'public':
                    self.session.execute(_CLOSED_BY_RQL,
                                         {'t': ticket.eid, 'r': rev.eid})
                    iwf = ticket.cw_adapt_to('IWorkflowable')
                    for tr in iwf.possible_transitions():
                        if tr.name in ('done', 'close'):
                            iwf.fire_transition(tr)
                            break

class RevisionAdded(hook.Hook):
    """Detect that a new revision is touched to prepare relevant operation

    On update we ignore non-phase change.
    """
    __regid__ = 'trackervcs.revision-to-ticket-state'
    __select__ = hook.Hook.__select__ & is_instance('Revision')
    events = ('after_add_entity', 'after_update_entity')
    category = 'autoset'

    def __call__(self):
        repo = self.entity.repository
        if not repo.reverse_source_repository:
            return
        if 'update' in self.event and 'phase' not in self.entity.cw_edited:
            return
        SearchRevisionTicketOp.get_instance(self._cw).add_data(self.entity.eid)


# synchronize  "P source_repository R" with ####################################
# "P has_apycot_environment PE AND PE local_repository R"

class SetSourceRepositoryOp(hook.Operation):
    """Automatically assign project repo to test env repo"""
    def precommit_event(self):
        if not self.project.source_repository and self.projectenv.repository:
            repo = self.projectenv.repository
            self.project.set_relations(source_repository=repo)

class ApycotEnvironmentAdded(hook.Hook):
    """Automatically assign project repo to test env repo"""
    __regid__ = 'trackervcs.add-source-repository'
    __select__ = hook.Hook.__select__ & hook.match_rtype('has_apycot_environment')
    events = ('after_add_relation',)
    category = 'autoset'

    def __call__(self):
        project = self._cw.entity_from_eid(self.eidfrom)
        if not project.source_repository:
            projectenv = self._cw.entity_from_eid(self.eidto)
            SetSourceRepositoryOp(self._cw, project=project, projectenv=projectenv)

# set ticket 'in-progress' when attached to a patch ############################

class PatchLinkedToTicket(hook.Hook):
    """Set ticket 'in-progress' when attached to a patch"""
    __regid__ = 'trackervcs.patch-linked-to-ticket'
    __select__ = hook.Hook.__select__ & hook.match_rtype('patch_ticket')
    events = ('after_add_relation',)
    category = 'autoset'

    def __call__(self):
        ticket = self._cw.entity_from_eid(self.eidto)
        ticket.cw_adapt_to('IWorkflowable').fire_transition_if_possible('start')

# attach patch to ticket on addition ###########################################

class PatchRevisionAdded(hook.Hook):
    """Attach patch to ticket on addition"""
    __regid__ = 'trackervcs.patch-revision-added'
    __select__ = hook.Hook.__select__ & hook.match_rtype('patch_revision')
    events = ('after_add_relation',)
    category = 'autoset'

    def __call__(self):
        patch = self._cw.entity_from_eid(self.eidfrom)
        rev = self._cw.entity_from_eid(self.eidto)
        source_repo = rev.repository
        eids = related_eids(rev.description)
        for ticket in tickets(self._cw, eids, source_repo.eid):
            # XXX should we drop existing links first?
            # We could just run the RQL below if there wasn't a cache issue
            # SET P patch_ticket T WHERE NOT P patch_ticket T, P eid ...
            if all(x.eid != ticket.eid for x in patch.patch_ticket):
                patch.set_relations(patch_ticket=ticket)


# security propagation #########################################################

# take care, code below may incidentally be propagated to nosylist.hooks.S_RELS
# depending on trackervcs/forge import order. Import order is fixed using
# __pkginfo__.__recommends__ so everything should be ok
tracker.S_RELS.add('source_repository')


# registration control #########################################################

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (RevisionAdded,
                                                     PatchLinkedToTicket,
                                                     PatchRevisionAdded,
                                                     ApycotEnvironmentAdded))
    if vreg.config['trusted-vcs-repositories']:
        vreg.register(RevisionAdded)

    if 'vcreview' in vreg.config.cubes():
        vreg.register(PatchLinkedToTicket)
        vreg.register(PatchRevisionAdded)
        # security propagation #################################################
        tracker.S_RELS |= set(('patch_revision', 'has_activity', ))
        tracker.O_RELS |= set(('point_of',))
    if 'apycot' in vreg.config.cubes():
        vreg.register(ApycotEnvironmentAdded)

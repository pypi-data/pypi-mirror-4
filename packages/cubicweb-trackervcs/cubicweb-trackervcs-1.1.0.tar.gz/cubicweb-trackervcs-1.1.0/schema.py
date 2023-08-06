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
"""cubicweb-trackervcs schema"""

from yams.buildobjs import RelationDefinition
from yams.reader import context

from cubicweb.schema import RQLConstraint


class source_repository(RelationDefinition):
    """version controled system holding sources for this project"""
    subject = 'Project'
    object = 'Repository'
    cardinality = '??'

class introduced_by(RelationDefinition):
    subject = 'Ticket'
    object = 'Revision'
    constraints = [RQLConstraint('S concerns P, O from_repository R, '
                                 'EXISTS(P source_repository R) OR EXISTS(P subproject_of PP, PP source_repository R)')]


class closed_by(RelationDefinition):
    subject = 'Ticket'
    object = 'Revision'
    constraints = [RQLConstraint('S concerns P, O from_repository R, '
                                 'EXISTS(P source_repository R) OR EXISTS(P subproject_of PP, PP source_repository R)')]

if 'Patch' in context.defined:
    from cubes.vcreview.schema import Patch
    from cubes.task.schema import Task

    class patch_ticket(RelationDefinition):
        subject = 'Patch'
        object = 'Ticket'
        constraints = [RQLConstraint('S patch_revision RE, '
                                     'RE from_repository R, '
                                     'O concerns P, '
                                     'EXISTS(P source_repository R) OR EXISTS(P subproject_of PP, PP source_repository R)')]


    class require_permission(RelationDefinition):
        subject = ('Patch', 'Task', 'InsertionPoint')
        object = 'CWPermission'

        Task.__permissions__.update({'add': ('managers', 'staff',),
                                     'update': ('managers', 'staff', 'owners')})
        Patch.__permissions__.update({'update': ('managers', 'staff')})

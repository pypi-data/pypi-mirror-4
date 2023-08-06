# -*- coding: utf-8 -*-
# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-queueing schema"""

from cubicweb.schema import RQLConstraint, WorkflowableEntityType

from yams.buildobjs import (EntityType, RelationType, SubjectRelation,
                            String, Float, Datetime)


class ResourceQueue(WorkflowableEntityType):
    name = String(required=True, unique=True, maxsize=64)


class QueueingEntity(EntityType):
    in_queue = SubjectRelation('ResourceQueue', cardinality='1*',
                               inlined=True, composite='object',
                               constraints=[RQLConstraint(
                                   'S has_qentity E, '
                                   'NOT EXISTS(QE in_queue O, QE has_qentity E, NOT S identity QE) ',
                                   msg=_('cannot queue the same entity twice'))])
    order = Float(required=True)


## RelationDefinition that must be implemented in concrete applications

class has_resources(RelationType):
    '''Relation between a ResourceQueue (subject) and the actual resource
    entity type (object), to be defined in concrete applications.'''
    subject = 'ResourceQueue'
    cardinality = '*?'


class has_qentity(RelationType):
    '''Relation between a QueueingEntity (subject) and the actual entity type
    that queue waiting for a resource to be available (object), to be defined
    in concrete applications.'''
    subject = 'QueueingEntity'
    inlined = True
    composite = 'object'
    cardinality = '1?'


class uses_resource(RelationType):
    '''
    Relation between the actual qentity entity type (subject) and the actual
    resource entity type (object), both to be defined in final applications.

    It must be set when the resource is busy because of the qentity.
    '''
    inlined = True
    cardinality = '??'
    constraints = (RQLConstraint('NOT EXISTS(QE has_qentity S)',
                                 msg=_('resource user cannot be in the queue at the same time')),)

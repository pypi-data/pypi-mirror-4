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

"""cubicweb-queueing entity's classes"""

import os.path as osp
from itertools import izip
import subprocess
import json

from cubicweb import InternalError
from cubicweb.predicates import (relation_possible, has_related_entities,
                                 is_instance, is_in_state)
from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.view import EntityAdapter

from cubes import queueing

class ResourceQueue(AnyEntity):
    __regid__ = 'ResourceQueue'

    def dc_title(self):
        initial = super(ResourceQueue, self).dc_title()
        resources = u', '.join([res.dc_title() for res in self.has_resources])
        return u'%s [%s]' % (initial, resources or u'empty')

    def __repr__(self):
        eids = ', '.join(str(e.eid) for e in self)
        return '<Entity %(cls)s %(eid)s [%(eids)s] at %(id)s>' \
               % dict(cls=self.__class__.__name__,
                      eid=self.eid, eids=eids, id=id(self))

    # workflow transition helpers

    def pause(self):
        wf_rq = self.cw_adapt_to('IWorkflowable')
        if wf_rq.state != 'pause':
            wf_rq.fire_transition('pause')

    def run(self):
        wf_rq = self.cw_adapt_to('IWorkflowable')
        if wf_rq.state != 'running':
            wf_rq.fire_transition('run')

    # queue object list handling methods

    def append(self, entity):
        '''q.append(e) <=> q.insert(0, e) [alias]
        append an entity to the end of the queue'''
        self.insert(len(self), entity)

    def remove(self, entity):
        '''Remove the entity from the queue.
        Raises ValueError if the entity is not present.'''
        rql = ('DELETE QueueingEntity QE '
               'WHERE QE in_queue Q, Q eid %(q)s, QE has_qentity E, E eid %(e)s')
        try:
            if not self._cw.execute(rql, {'q': self.eid, 'e': entity.eid}).rowcount:
                raise ValueError('not in queue: %r' % entity)
        except AttributeError:
            raise ValueError('not in queue: %r' % entity)
        self.cw_clear_relation_cache('in_queue', 'object')

    def __iter__(self):
        rql = ('Any E,QE,Q ORDERBY O WHERE QE in_queue Q, Q eid %(eid)s, '
               'QE order O, QE has_qentity E')
        return self._cw.execute(rql, {'eid': self.eid}).entities()

    def __len__(self):
        """len(q) <=> q.__len__()
        Return the number of entities still queued.
        """
        return len(self.reverse_in_queue)

    def __nonzero__(self):
        "do not let standard bool() call sequence return 0 if len is 0"
        return True

    def _insert_order(self, pos):
        '''Return order value to be given to an entity to insert it at the
        given position
        '''
        qlen = len(self)
        if qlen == 0:
            return 0

        ctx = {'eid':self.eid}
        rql = ('Any O ORDERBY O ASC LIMIT %s OFFSET %s '
               'WHERE QE in_queue Q, Q eid %%(eid)s, QE order O')

        if pos < 0:
            pos = 0 if (-pos > qlen) else (qlen + pos)

        if pos == 0:
            order = self._cw.execute(rql % (1, 0), ctx)[0][0]
            return order -1

        if pos >= qlen:
            order = self._cw.execute(rql % (1, qlen -1), ctx)[0][0]
            return  order + 1

        orders = (d[0] for d in self._cw.execute(rql % (2, pos - 1), ctx))
        return sum(orders) / 2

    def insert(self, position, entity):
        'insert ``entity`` before position.'
        order = self._insert_order(position)
        self.cw_clear_relation_cache('in_queue', 'object')
        self._cw.create_entity('QueueingEntity', in_queue=self, order=order,
                               has_qentity=entity)


class QueueingEntity(AnyEntity):
    __regid__ = 'QueueingEntity'

    fetch_attrs, cw_fetch_order = fetch_config(['order', 'has_qentity'])

    def dc_title(self):
        return self._cw._(u'Queued %s') % self.has_qentity[0].dc_title()

    @property
    def qentity(self):
        return self.has_qentity[0]


class Queueable(EntityAdapter):
    """
    Default adapter for the entity types that are meant to use the resources
    that the ResourceQueue instances manage (i.e. the 'qentities').

    It has two distinct roles:

    * determine if the current qentity can use a given resource; the answer is
      True by default, see the `can_use_resource` method

    * handle the `uses_resource` relation and dispatch the other actions to be
      performed when a qentity starts and stops using a resource.
    """
    __regid__ = 'Queueable'
    __select__ = (EntityAdapter.__select__ &
                  relation_possible('has_qentity', role='object', action=None))

    def can_use_resource(self, resource):
        '''
        Tells whether current queued entity can use the passed resource
        or not.
        '''
        return True

    def prepare_authentication(self):
        """ not really a security scheme: we give the adapted entity eid """
        return self.entity.eid

    def authenticate(self, login, authobj, **kwargs):
        """ default authentication: same adapted entity than at
        preparation time """
        return self.entity.eid == int(authobj)

    @property
    def use_async(self):
        has_zmq = bool(self._cw.vreg.config['zmq-repository-address'])
        self.debug('Use asynchronous process for resource queue %s ? %s',
                   self.entity.dc_title(), has_zmq)
        return has_zmq

    def acquire_resource(self, resource):
        ''' Remove entity from queue and start it on resource `resource`. '''
        qresource = resource.cw_adapt_to('QResource')
        assert qresource, ('did you just forget to provide a '
                           'Qresource adapter for thgis entity ?')
        # remove `queuing` entity from queue
        self.entity.reverse_has_qentity[0].cw_delete()
        self.entity.set_relations(uses_resource=resource)
        assert resource.reverse_has_resources, self._cw._(
            'resource %s has no queue') % resource
        self.info('starting %s on resource %s', self.entity, resource)
        if self.use_async:
            async_path = osp.join(osp.abspath(osp.dirname(queueing.__file__)),
                                  "async.py")
            authobject = self.prepare_authentication()
            callargs = [str(arg) for arg in
                        ['python',
                         async_path,
                         self._cw.vreg.config.appid,
                         self._cw.vreg.config['zmq-repository-address'],
                         resource.eid,
                         self.entity.eid,
                         self.entity.created_by[0].login,
                         json.dumps(authobject),
                         self._cw.vreg.config.mode]]
            self.info('subprocess call with: %s', ', '.join(callargs))
            def deferred():
                subprocess.Popen(callargs)
            return deferred
        else:
            # XXX to deprecate ?
            def deferred():
                with self._cw.repo.internal_session() as session:
                    efi = session.entity_from_eid
                    qresource = efi(resource.eid).cw_adapt_to('QResource')
                    entity = efi(self.entity.eid)
                    qresource.execute(entity)
                    session.commit()
            return deferred

    def release_resource(self):
        '''
        Release resource used by current entity (raises IndexError if it does
        not use any). Tells the scheduler it can now assign the freed resource.
        '''
        res = self.entity.uses_resource[0]
        self.info('releasing resource %s on resource %s', self.entity, res)
        self.entity.set_relations(uses_resource=None)


class QResource(EntityAdapter):
    """
    Abstract adapter that aims at exposing the API that must be implemented in
    final applications to manage the association between a queueing entity and
    a resource: how to use the resource, how to force disassociation, a.s.o.
    """
    __regid__ = 'QResource'
    __abstract__ = True
    __select__ = (EntityAdapter.__select__ &
                  has_related_entities('has_resources', 'object', 'ResourceQueue'))

    def execute(self, qentity):
        '''
        Implement here what you need to actually execute code using
        current resource with entity `qentity`.
        '''
        raise NotImplementedError


class QTrivialScheduler(EntityAdapter):
    __regid__ = 'QScheduler'
    __select__ = (EntityAdapter.__select__ & is_instance('ResourceQueue')
                  & is_in_state('running'))

    def distribute_resources(self, only=()):
        """
        Assign resources to queuing entities.

        If the `only` parameter is a non empty sequence, the scheduler
        only considers distributing the listed resources.
        """
        self.debug('QTrivialScheduler asked to distribute resources')
        only = tuple(self._cw.entity_from_eid(res) for res in only)
        deferred = []
        for res in (only or self.entity.has_resources):
            if res.reverse_uses_resource:
                self.debug('QTrivialScheduler : resource %s is *busy*', res)
                continue
            self.debug('QTrivialScheduler : resource %s is *free*', res)
            for qent in self.entity:
                queueable = qent.cw_adapt_to('Queueable')
                if queueable.can_use_resource(res):
                    self.info('QTrivialScheduler: assign %s to %s', res, qent)
                    deferred.append(queueable.acquire_resource(res))
                    break
        return deferred

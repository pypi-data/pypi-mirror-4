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

"""cubicweb-queueing specific hooks and operations"""


from cubicweb import AuthenticationError
from cubicweb.predicates import on_fire_transition
from cubicweb.server import hook
from cubicweb.server.hook import (Hook, LateOperation, DataOperationMixIn,
                                  match_rtype)


class DistributeResourcesOp(DataOperationMixIn, LateOperation):
    '''
    Late operation that redistributes the resources that have been freed at some
    point in the transaction, taking into account any non-late operation that
    user cubes may use to remove/ insert queueing entities.
    '''

    def postcommit_event(self):
        deferred = []
        with self.session.repo.internal_session() as session:
            data = list(self.get_data())
            complete_redistribution = set(r for (r, only) in data
                                          if not only)
            for (res, only) in data:
                # distribute resources only once if one call at least considers all
                if not only or res not in complete_redistribution:
                    scheduler = session.entity_from_eid(res).cw_adapt_to('QScheduler')
                    # Let a chance to user-cubes not to schedule on this resource
                    # (for example if not ready), by overriding default scheduler
                    # selector; this is the reason why we choose not to crash here
                    if scheduler:
                        self.info('asking scheduler %s to distribute resources (%s)',
                                  scheduler, only or scheduler.entity.has_resources)
                        deferred += scheduler.distribute_resources(only=only)
            session.commit()
        self.info('%s callbacks to run', len(deferred))
        for callback in deferred:
            self.info('launching callback %s', callback)
            callback()

class NewQueuedEntityHook(Hook):
    __regid__ = 'queueing.new_queued_entity'
    __select__ = Hook.__select__ & match_rtype('in_queue')
    events = ('after_add_relation',)

    def __call__(self):
        queue = self._cw.entity_from_eid(self.eidto)
        self.info('new queued entity: asking for resource distribution '
                  'for queue %s', queue)
        DistributeResourcesOp.get_instance(self._cw).add_data((queue.eid, ()))


class ResourceQueueRunTransition(Hook):
    __regid__ = 'queueing.resource_queue_run_transition'
    __select__ = Hook.__select__ & on_fire_transition('ResourceQueue', 'run')
    events = ('after_add_entity',)

    def __call__(self):
        queue = self.entity.for_entity
        self.info('queue run transition passed: asking for resource '
                  'distribution for queue %s', queue)
        DistributeResourcesOp.get_instance(self._cw).add_data((queue.eid, ()))


class NewResourceForQueueHook(Hook):
    __regid__ = 'queueing.new_resource_for_queue'
    __select__ = Hook.__select__ & match_rtype('has_resources')
    events = ('after_add_relation',)

    def __call__(self):
        queue = self._cw.entity_from_eid(self.eidfrom)
        res = self._cw.entity_from_eid(self.eidto)
        self.info('new resource %s in queue %s: asking resource distribution',
                  res, queue)
        DistributeResourcesOp.get_instance(self._cw).add_data((queue.eid, (res.eid,)))


class ResourceReleasedHook(Hook):
    __regid__ = 'queueing.resource_released'
    __select__ = Hook.__select__ & match_rtype('uses_resource')
    events = ('after_delete_relation',)

    def __call__(self):
        res = self._cw.entity_from_eid(self.eidto)
        queue = res.reverse_has_resources[0]
        self.info('resource %s (queue %s) released: asking resource '
                  'distribution', res, queue)
        DistributeResourcesOp.get_instance(self._cw).add_data((queue.eid, (res.eid,)))




from cubicweb.server.sources import native

class QueueableAuthentifier(native.LoginPasswordAuthentifier):
    """ a source authentifier plugin for queueables """

    def authenticate(self, session, login, **kwargs):
        """ delegates authentication to a Queueable adapter """
        session.debug('authentication by %s', self.__class__.__name__)
        queueableeid = kwargs.get('queueable_eid')
        if queueableeid:
            try:
                queueable = session.entity_from_eid(queueableeid)
                adapter = queueable.cw_adapt_to('Queueable')
                if adapter.authenticate(login=login, **kwargs):
                    return session.execute('CWUser U WHERE U login %(login)s',
                                           {'login': login}).rows[0][0]
            except Exception, exc:
                session.debug('authentication failure (%s)', exc)
        raise AuthenticationError('%s user not authentified', login)


class ServerStartupHook(hook.Hook):
    """ register the foo authenticator """
    __regid__ = 'queueableauthenticatorregisterer'
    events = ('server_startup',)

    def __call__(self):
        self.debug('registering queueable authentifier')
        self.repo.system_source.add_authentifier(QueueableAuthentifier())

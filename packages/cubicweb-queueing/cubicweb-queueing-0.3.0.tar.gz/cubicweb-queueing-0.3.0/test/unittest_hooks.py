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

import time

from cubicweb.devtools.testlib import CubicWebTC

from cubes.queueing.entities import Queueable
from cubes.queueing.testutils import zmq_server_launch, QueueingTestMixin

class QueueingHookTC(QueueingTestMixin, CubicWebTC):

    def test_async(self):
        self.queue1.run()
        self.commit()
        with zmq_server_launch(self.config, self.repo):
            self.queue1.append(self.run1)
            self.commit()
            # wait for async process completion
            t0, max_wait_seconds, check_interval_seconds = time.time(), 10, 0.5
            while time.time() < t0 + max_wait_seconds:
                time.sleep(check_interval_seconds)
                req = self.request()
                if req.execute('Any R,D WHERE R is Run, R eid %s, R done D' %
                               self.run1.eid):
                    break
                print '.',
            else:
                self.fail('asynchronous job max waiting time reached')
        self.queue1.cw_clear_all_caches()
        self.run1.cw_clear_all_caches()
        self.assertEqual(len(self.queue1), 0)
        # Yes: nobody actually releases the resource !
        self.assertEqual(len(self.run1.uses_resource), 1)

    def test_new_qentity(self):
        self.queue1.run()
        self.commit()
        self.queue1.append(self.run1)
        self.commit()
        self.assertEqual(len(self.queue1), 0)
        self.assertEqual(len(self.run1.uses_resource), 1)

    def test_queue_run_transition(self):
        self.queue1.append(self.run1)
        self.commit()
        self.queue1.run()
        self.commit()
        self.assertEqual(len(self.queue1), 0)
        self.assertEqual(len(self.run1.uses_resource), 1)

    def test_new_resource(self):
        # run a queue with 2 resources and 3 jobs
        self.queue1.append(self.run1)
        self.queue1.append(self.run2)
        self.queue1.append(self.run3)
        self.queue1.run()
        self.commit()
        # check the two first-in jobs have a resource, and that
        # the third has not and is still in the queue
        self.assertQEntityUsesResource(self.run1)
        self.assertQEntityUsesResource(self.run2)
        self.assertQEntityUsesNoResource(self.run3)
        self.assertQEntitiesEqual(self.queue1, [self.run3])
        # check adding a resource consumes the third job
        self.queue1.set_relations(has_resources=self.host3)
        self.commit()
        self.assertEqual(len(self.queue1), 0)
        self.assertQEntityUsesResource(self.run3)

    def test_resource_released(self):
        # add two jobs in the queue with self.host1 as a single resource
        self.host2.set_relations(reverse_has_resources=None)
        self.queue1.run()
        self.queue1.append(self.run1)
        self.queue1.append(self.run2)
        self.commit()
        # release resource and check next job takes over
        self.run1.cw_adapt_to('Queueable').release_resource()
        self.commit()
        self.assertQEntityUsesResource(self.run2)
        self.assertEqual(self.run2.uses_resource[0].eid, self.host1.eid)


class FunctionalTC(QueueingTestMixin, CubicWebTC):

    def test_cannot_use(self):
        self.queue1.run()
        self.commit()
        orig_method = Queueable.can_use_resource
        try:
            Queueable.can_use_resource = lambda self, resource: False
            self.queue1.append(self.run1)
            self.commit()
        finally:
            Queueable.can_use_resource = orig_method
        self.assertQEntitiesEqual(self.queue1, [self.run1])
        # restart queue to recheck can_use_resource effect
        self.queue1.pause()
        self.commit()
        self.queue1.run()
        self.commit()
        self.assertEqual(len(self.queue1), 0)


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

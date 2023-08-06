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


from cubicweb.devtools.testlib import CubicWebTC

from cubes.queueing.entities import Queueable
from cubes.queueing.testutils import QueueingTestMixin


class ResourceQueueTC(QueueingTestMixin, CubicWebTC):

    def test_len(self):
        q = self.queue1
        q.cw_clear_relation_cache('in_queue', 'object')
        self.assertEqual(len(q), 0)
        self.create_entity('QueueingEntity', in_queue=q, order=0.0, has_qentity=self.run1)
        q.cw_clear_relation_cache('in_queue', 'object')
        self.assertEqual(len(q), 1)
        self.create_entity('QueueingEntity', in_queue=q, order=1.5, has_qentity=self.run3)
        q.cw_clear_relation_cache('in_queue', 'object')
        self.assertEqual(len(q), 2)
        self.create_entity('QueueingEntity', in_queue=q, order=2.0, has_qentity=self.run2)
        q.cw_clear_relation_cache('in_queue', 'object')
        self.assertEqual(len(q), 3)

    def test_insert(self):
        q = self.queue1
        q.insert(0, self.run1) # cache on `in_aueue` already cleared
        q.insert(10, self.run3)
        q.insert(1, self.run2)
        self.assertQEntitiesEqual(q, [self.run1, self.run2, self.run3])

        r4 = self.create_entity('Run', name=u'r4')
        r5 = self.create_entity('Run', name=u'r5')
        r6 = self.create_entity('Run', name=u'r6')
        q.insert(-10, r4) # cache on `in_aueue` already cleared
        q.insert(-1, r5)
        q.insert(-2, r6)
        self.assertQEntitiesEqual(q, [r4, self.run1, self.run2, r6, r5, self.run3])

    def test_append(self):
        q = self.queue1
        q.append(self.run1)
        q.append(self.run2)
        q.append(self.run3)
        self.assertQEntitiesEqual(q, [self.run1, self.run2, self.run3])


    def test_remove(self):
        q = self.queue1
        self.assertRaises(ValueError, q.remove, 0)
        self.assertRaises(ValueError, q.remove, self.run1)
        q.append(self.run1)
        q.remove(self.run1)
        self.assertEqual(len(q), 0)
        q.append(self.run1)
        q.append(self.run2)
        q.append(self.run3)
        q.remove(self.run2)
        self.assertQEntitiesEqual(q, [self.run1, self.run3])
        self.assertRaises(ValueError, q.remove, self.run2)
        q.remove(self.run1)
        q.remove(self.run3)
        self.assertEqual(len(q), 0)

    def test_iter(self):
        q = self.queue1
        q.append(self.run1)
        q.append(self.run2)
        q.append(self.run3)

        self.assertEqual([r.eid for r in q], [self.run1.eid, self.run2.eid, self.run3.eid])
        self.assertEqual(len(q), 3)

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

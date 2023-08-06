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

from cubicweb import ValidationError
from cubicweb.devtools.testlib import CubicWebTC


class SchemaTC(CubicWebTC):

    def setup_database(self):
        super(SchemaTC, self).setup_database()
        ce = self.request().create_entity
        self.h = ce('Host', name=u'h1')
        self.q = ce('ResourceQueue', name=u'queue1', has_resources=self.h)
        self.r = ce('Run', name=u'r1')
        self.commit()

    def assertErrorMsg(self, cm, msg):
        self.assertTrue(str(cm.exception).endswith(msg))

    def test_resource_user_is_no_more_queueing(self):
        'an entity that uses a resource cannot queue at the same time'
        self.q.append(self.r)
        self.commit()
        with self.assertRaises(ValidationError) as cm:
            self.r.set_relations(uses_resource=self.h)
            self.commit()
        self.assertErrorMsg(cm, 'resource user cannot be in the queue at the same time')
        self.rollback()

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

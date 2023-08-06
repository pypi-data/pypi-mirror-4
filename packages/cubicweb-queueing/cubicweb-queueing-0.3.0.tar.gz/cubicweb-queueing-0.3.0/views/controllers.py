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
"""cubicweb-queueing controllers"""

from cubicweb import UnknownEid
from cubicweb.web.views.ajaxcontroller import ajaxfunc


@ajaxfunc(output_type='json')
def move_queued_entity(self, rqueue_eid, qentity_eid, dest_index):
    rqueue = self._cw.entity_from_eid(rqueue_eid)
    qentity = self._cw.entity_from_eid(qentity_eid)
    self.debug('move entity %(qe)s to new position %(to)i within queue %(rq)s' %
               {'rq': rqueue, 'qe': qentity, 'to': dest_index})
    rqueue.remove(qentity)
    rqueue.insert(dest_index, qentity)
    return True

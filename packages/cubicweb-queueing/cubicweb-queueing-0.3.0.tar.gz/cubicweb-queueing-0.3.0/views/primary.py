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

"""cubicweb-queueing views/forms/actions/components for web ui"""

from cubicweb.predicates import is_instance
from cubicweb.web.views import primary
from cubicweb.web.views import baseviews
from cubicweb.tags import tag

P = tag('p') # xml_escaped

class PrimaryView(primary.PrimaryView):
    __select__ = primary.PrimaryView.__select__ & is_instance('ResourceQueue')
    onload = '$("#%s").sortable({cursor:"move", update:cw.cubes.queueing.onUpdateSortableResourceQueue});'
    item_vid = 'text'

    def render_entity_attributes(self, entity):
        req = self._cw
        req.add_js(('cubes.queueing.js', 'jquery.ui.js',))
        req.add_css(('cubes.queueing.css', 'jquery.ui.css',))

        listid = 'rq-%d' % entity.eid
        req.add_onload(self.onload % listid)

        rset = entity.related('in_queue', 'object')
        if rset:
            self.wview('list', subvid=self.item_vid,
                       rset=entity.related('in_queue', 'object'),
                       listid=listid, klass='sortable_resource_queue')
        else:
            self.w(P(req._('empty queue')))


class QEListView(baseviews.ListView):
    __select__ = baseviews.ListView.__select__ & is_instance('QueueingEntity')

    def cell_call(self, row, col=0, vid=None, **kwargs):
        self.w(u'<li id="qe-%d">' % self.cw_rset.get_entity(row, col).qentity.eid)
        self.wview(self.item_vid, self.cw_rset, row=row, col=col, vid=vid, **kwargs)
        self.w(u'</li>\n')


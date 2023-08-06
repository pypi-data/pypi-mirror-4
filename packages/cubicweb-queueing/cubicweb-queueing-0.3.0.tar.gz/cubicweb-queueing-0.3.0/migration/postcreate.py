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

"""cubicweb-queueing postcreate script, executed at instance creation time or when
the cube is added to an existing instance.

You could setup site properties or a workflow here for example.
"""

rq_wf = add_workflow(u'resource queue workflow', 'ResourceQueue')

paused = rq_wf.add_state(_('paused'), initial=True)
running = rq_wf.add_state(_('running'))

rq_wf_perms = ('managers',)
rq_wf.add_transition(_('run'), (paused,), running, rq_wf_perms)
rq_wf.add_transition(_('pause'), (running,), paused, rq_wf_perms)

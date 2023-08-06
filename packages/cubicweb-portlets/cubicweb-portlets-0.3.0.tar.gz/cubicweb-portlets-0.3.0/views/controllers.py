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

"""cubicweb-portlets controllers"""

from cubicweb.web.views.ajaxcontroller import ajaxfunc


@ajaxfunc(output_type='json')
def save_portlet_state(self, portlet_eid, attrs):
    portlet = self._cw.entity_from_eid(portlet_eid)
    assert portlet.__regid__ == 'Portlet'
    portlet.set_attributes(**attrs)


@ajaxfunc(output_type='json')
def save_portal_columns_state(self, column_states):
    self.debug('save_portal_column_state states: %s', column_states)
    eeid = self._cw.entity_from_eid
    # First remove portlets of the concerned columns to avoid duplicate keys
    columns = {}
    for state in column_states:
        column = columns[state['eid']] = eeid(state['eid'])
        assert column.__regid__ == 'PortalColumn'
        column.set_relations(reverse_in_column=None)
    # Then renumber portlets and link them to their new column
    for state in column_states:
        column = columns[state['eid']]
        for order, peid in enumerate(state['portlet_eids']):
            eeid(peid).set_attributes(order=order)
        if state['portlet_eids']: # could be empty
            column.set_relations(reverse_in_column=state['portlet_eids'])
    return True

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

"""cubicweb-portlets entity's classes"""


from cubicweb.entities import AnyEntity, fetch_config

class Portal(AnyEntity):
    __regid__ = 'Portal'


    def unrelated_portlets(self):
        rql = ('Any P WHERE P is Portlet, X eid %(x)s, '
               'NOT EXISTS(P in_column C, C in_portal X)')
        return self._cw.execute(rql, {'x': self.eid})


class Portlet(AnyEntity):
    __regid__ = 'Portlet'
    fetch_attrs, cw_fetch_order = fetch_config(
        ['name', 'color', 'order', 'content', 'in_column'], mainattr='order')


class PortalColumn(AnyEntity):
    __regid__ = 'PortalColumn'
    fetch_attrs, cw_fetch_order = fetch_config(['order', 'size', 'in_portal'])

    @property
    def portal(self):
        return self.in_portal[0]

    def dc_title(self):
        return '%s #%s (size: %s)' % (self.portal.dc_title(), self.order, self.size)

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

"""cubicweb-portlets primary views"""

from cubicweb.predicates import is_instance
from cubicweb.web.views.primary import PrimaryView

from cubes.portlets.views.mixins import PortletContainerMixin


class PortalPrimaryView(PortletContainerMixin, PrimaryView):
    __select__ = PrimaryView.__select__ & is_instance('Portal')

    def unrelated_portlets(self, entity):
        rset = entity.unrelated_portlets()
        button_content = self._cw._('other portlets')
        self.w(u'<div class="unrelated-portlets">'
               u'<span class="button"><a href="#">+</a>%s</span>'
               u'<ul class="column">' % button_content)
        self.render_portlets(rset.entities(0))
        self.w(u'</ul></div>')

    def render_entity(self, entity):
        if entity.cw_has_perm('update'):
            self._cw.add_js(('jquery.js', 'jquery.ui.js', 'cubes.portlets.js'))
            self._cw.add_onload("iNettuts.init.apply(iNettuts);");
        self._cw.add_css('cubes.portlets.css')
        self.w(u'<div id="columns">')
        self.unrelated_portlets(entity)
        columns = entity.reverse_in_portal
        if columns:
            total_size = sum(c.size for c in columns)
            for column in columns:
                size = 100 * column.size / total_size
                self.wview('portalcolumn_in_portal', rset=column.as_rset(),
                           size=size)
        self.w(u'</div>')

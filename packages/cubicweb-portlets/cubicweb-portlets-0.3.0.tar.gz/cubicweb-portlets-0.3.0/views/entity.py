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

"""cubicweb-portlets entity views"""


from logilab.mtconverter import xml_escape

from cubicweb.predicates import is_instance
from cubicweb.view import EntityView

from cubes.portlets.views.mixins import PortletContainerMixin


class PortalColumnInPortalView(PortletContainerMixin, EntityView):
    __regid__ = 'portalcolumn_in_portal'
    __select__ = EntityView.__select__ & is_instance('PortalColumn')

    def entity_call(self, entity, size=100.):
        self.w(u'<ul id="portlet-column-%s" class="column" style="width:%s%%">'
               % (entity.eid, size))
        portlets = entity.reverse_in_column
        self.render_portlets(portlets)
        self.w(u'</ul>')


class PortletInPortalView(EntityView):
    __regid__ = 'portlet_in_portal'
    __select__ = EntityView.__select__ & is_instance('Portlet')

    def dom_id(self, entity):
        'return dom id of the portlet content; will be escaped before insertion'
        return u'portlet-%s' % entity.eid

    def content(self, entity):
        'return *html content* (so it is not further escaped)'
        return entity.content

    def entity_call(self, entity):
        ctx = dict(title=xml_escape(entity.name),
                   dom_id=xml_escape(self.dom_id(entity)),
                   content=self.content(entity))
        self.w(u'<div class="widget-head">\n'
               u' <h3>%(title)s</h3>\n'
               u'</div>\n'
               u'<div id="%(dom_id)s" class="widget-content">\n'
               u' %(content)s\n'
               u'</div>' % ctx)

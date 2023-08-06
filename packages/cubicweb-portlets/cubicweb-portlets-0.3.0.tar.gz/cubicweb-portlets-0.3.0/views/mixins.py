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

"""cubicweb-portlets views mixins"""


class PortletContainerMixin(object):

    def li_placeholder(self):
        self.w(u'')

    def render_portlets(self, portlets):
        if portlets:
            for portlet in portlets:
                self.w(u'<li class="widget %scolor-%s">'
                       % (portlet.collapsed and u'collapsed ' or u'', portlet.color))
                self.wview('portlet_in_portal', rset=portlet.as_rset())
                self.w(u'</li>')
        else:
            self.w(u'<li style="display:none">placeholder</li>')

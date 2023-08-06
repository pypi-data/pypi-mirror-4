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

"""cubicweb-portlets views/forms/actions/components for web ui"""


from cubicweb.web import uicfg

_afs = uicfg.autoform_section
_affk = uicfg.autoform_field_kwargs
_pvs = uicfg.primaryview_section


_afs.tag_object_of(('PortalColumn', 'in_portal', 'Portal'), 'main', 'inlined')
_afs.tag_subject_of(('Portlet', 'in_column', 'PortalColumn'), 'main', 'attributes')
_afs.tag_subject_of(('Portlet', 'in_column', 'PortalColumn'), 'muledit', 'attributes')

_pvs.tag_subject_of(('Portlet', 'in_column', 'PortalColumn'), 'sideboxes')

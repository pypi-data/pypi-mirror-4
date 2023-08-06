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

"""cubicweb-portlets schema"""

from yams.buildobjs import (EntityType, SubjectRelation,
                            Int, String, RichString, Float, Boolean)
from yams.constraints import RegexpConstraint, BoundConstraint


class Portal(EntityType):

    name = String(required=True, maxsize=128)


class Portlet(EntityType):
    __unique_together__ = [('in_column', 'order')]

    name = String(required=True, maxsize=255)
    color = String(required=True, maxsize=6, internationalizable=True,
                   vocabulary=[_('yellow'), _('red'), _('blue'),
                               _('white'), _('orange'), _('green')])
    order = Int(required=True)
    collapsed = Boolean(required=True, default=False)
    content = RichString(required=True, default_format='text/plain')
    for_portal = SubjectRelation('Portal', cardinality='1*',
                                 inlined=True, composite='object')
    in_column = SubjectRelation('PortalColumn', cardinality='?*', inlined=True)


class PortalColumn(EntityType):
    """ portals have a rigid column layout """
    __unique_together__ = [('in_portal', 'order')]

    order = Int(required=True,
                constraints=[BoundConstraint('>=', 0)])
    in_portal = SubjectRelation('Portal', cardinality='1*', inlined=True,
                                composite='object')
    size = Float(required=True,
                 description="percentage size of the container")

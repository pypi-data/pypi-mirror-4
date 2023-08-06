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

from simplejson import dumps

from cubicweb.devtools.testlib import CubicWebTC


class SavePortalColumnsStateTC(CubicWebTC):

    def setup_database(self):
        super(SavePortalColumnsStateTC, self).setup_database()
        ce = self.request().create_entity
        self.portal = ce('Portal', name=u'test portal')
        p = self.portal
        self.cols = {'c0': ce('PortalColumn', order=0, in_portal=p, size=1.),
                     'c1': ce('PortalColumn', order=1, in_portal=p, size=1.)}
        c0, c1 = self.cols['c0'], self.cols['c1']
        ct, co = u'<p>content</p>', u'red'
        self.portlets = {'p00': ce('Portlet', name=u'p00', order=0, color=co,
                                   collapsed=False, content=ct, in_column=c0,
                                   for_portal=p),
                         'p10': ce('Portlet', name=u'p10', order=1, color=co,
                                   collapsed=False, content=ct, in_column=c0,
                                   for_portal=p),
                         'p01': ce('Portlet', name=u'p01', order=0, color=co,
                                   collapsed=False, content=ct, in_column=c1,
                                   for_portal=p),
                         'p11': ce('Portlet', name=u'p11', order=1, color=co,
                                   collapsed=False, content=ct, in_column=c1,
                                   for_portal=p),
                         'p21': ce('Portlet', name=u'p21', order=2, color=co,
                                   collapsed=False, content=ct, in_column=c1,
                                   for_portal=p),
                         }
        self.commit()

    def ajax_call(self, states):
        req = self.request()
        req.form = {'fname': u'save_portal_columns_state', 'arg': dumps(states)}
        ctrl = self.vreg['controllers'].select('ajax', req=req, appli=self.app)
        return ctrl.publish()

    def test_move_portlet(self):
        # move p11 from c1 to c0
        _c = lambda name: self.cols[name].eid
        _p = lambda name: self.portlets[name].eid
        states = [
            dict(eid=_c('c1'), portlet_eids=[_p('p01'), _p('p21')]),
            dict(eid=_c('c0'), portlet_eids=[_p('p00'), _p('p10'), _p('p11')]),
            ]
        self.assertTrue(self.ajax_call(states))
        self.assertEqual(self.portlets['p11'].in_column[0].eid, _c('c0'))
        # move all portlets to c0 (makes one column empty)
        states = [
            dict(eid=_c('c1'), portlet_eids=[]),
            dict(eid=_c('c0'), portlet_eids=[_p('p00'), _p('p10'), _p('p11'),
                                             _p('p01'), _p('p21')]),
            ]
        self.assertTrue(self.ajax_call(states))
        for p in self.portlets.itervalues():
            self.assertEqual(p.in_column[0].eid, _c('c0'))
        self.assertEqual(len(self.cols['c1'].reverse_in_column), 0)
        # move inside same column
        states = [
            dict(eid=_c('c1'), portlet_eids=[]),
            dict(eid=_c('c0'), portlet_eids=[_p('p00'), _p('p10'), _p('p11'),
                                             _p('p21'), _p('p01')]),
            ]
        self.assertTrue(self.ajax_call(states))

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

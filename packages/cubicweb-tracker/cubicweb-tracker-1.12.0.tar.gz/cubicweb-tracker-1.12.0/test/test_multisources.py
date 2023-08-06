from datetime import timedelta

from cubicweb import MultiSourcesError
from cubicweb.devtools.testlib import CubicWebTC

from cubes.tracker.testutils import BaseMSTC, ms_test_init

class ThreeSourcesTC(BaseMSTC):

    def test_projects_list(self):
        rset = self.execute('Project P')
        self.assertEqual(len(rset), 6)

    def test_nonregr1(self):
        rset = self.execute('Any X WHERE X eid %(x)s, V version_of X, V in_state S, S name "published"',
                            {'x': self.ip1eid})
        self.assertEqual(rset.rows, [])
        self.change_state(self.ip1v1eid, 'published')
        rset = self.execute('Any X WHERE X eid %(x)s, V version_of X, V in_state S, S name "published"',
                            {'x': self.ip1eid})
        self.assertEqual(len(rset.rows), 1)
        self.assertEqual(rset.rows[0][0], self.ip1eid)
        rset = self.execute('Any X WHERE X eid %(x)s, V version_of X, V in_state S, S name "published"',
                            {'x': self.ip2eid})
        self.assertEqual(rset.rows, [])
        self.change_state(self.ip2v1eid, 'published')
        rset = self.execute('Any X WHERE X eid %(x)s, V version_of X, V in_state S, S name "published"',
                            {'x': self.ip2eid})
        self.assertEqual(len(rset.rows), 1)
        # same test with entities from the external source
        iep1eid = self.extid2eid(ep1eid, 'Project')
        iep1v1eid = self.extid2eid(ep1v1eid, 'Project')
        rset = self.execute('Any X WHERE X eid %(x)s, V version_of X, V in_state S, S name "published"',
                            {'x': iep1eid})
        self.assertEqual(rset.rows, [])
        # XXX don't work anymore since changing state is done by adding TrInfo which isn't currently
        #     imported from external sources
        self.assertRaises(MultiSourcesError, self.change_state, iep1v1eid, 'published')
        #self.change_state(iep1v1eid, 'published')
        # rset = self.execute('Any X WHERE X eid %(x)s, V version_of X, V in_state S, S name "published"',
        #                     {'x': iep1eid})
        # self.assertEqual(len(rset.rows), 1, rset)
        # self.assertEqual(rset.rows[0][0], iep1eid)
        # iep2eid = self.extid2eid(ep2eid, 'Project')
        # iep2v1eid = self.extid2eid(ep2v1eid, 'Project')
        # rset = self.execute('Any X WHERE X eid %(x)s, V version_of X, V in_state S, S name "published"',
        #                     {'x': iep2eid})
        # self.assertEqual(rset.rows, [])
        # self.change_state(iep2v1eid, 'published')
        # rset = self.execute('Any X WHERE X eid %(x)s, V version_of X, V in_state S, S name "published"',
        #                     {'x': iep2eid})
        # self.assertEqual(len(rset.rows), 1)

    def test_nonregr2(self):
        ip2v1 = self.execute('Any X WHERE X eid %(x)s', {'x': self.ip2v1eid}).get_entity(0, 0)
        rset = ip2v1.depends_on_rset()
        self.assertEqual(len(rset.rows), 1)
        self.assertEqual(rset.rows[0][0], self.ip1v1eid)

    def test_nonregr3(self):
        self.execute('Any V,DATE ORDERBY version_sort_value(N) '
                     'WHERE V num N, V prevision_date DATE, V version_of X, '
                     'V in_state S, S name IN ("planned", "dev", "ready"), X eid %(x)s',
                     {'x': self.ip1eid})

    def test_nonregr4(self):
        # test we can a change a ticket state (and implicitly its version'state by commiting
        self.fire_transition(self.ip1t1eid, 'start')
        self.commit()
        ip1v1 = self.execute('Any X WHERE X eid %(x)s', {'x': self.ip1v1eid}).get_entity(0, 0)
        self.assertEqual(ip1v1.cw_adapt_to('IWorkflowable').state, 'dev')

    def test_nonregr5(self):
        self.fire_transition(self.ip1t1eid, 'start')
        self.commit()
        rset = self.execute('Any X,U WHERE X in_state S, S name "in-progress", TR wf_info_for X, TR to_state S, TR owned_by U')
        self.assertEqual(len(rset), 1, rset.rows)
        self.assertEqual(rset[0], [self.ip1t1eid, self.session.user.eid])

    def test_nonregr7(self):
        rset = self.execute('Any B,TT,NOW - CD,PR,S,V '
                            'GROUPBY B,TT,CD,PR,S,V,VN '
                            'ORDERBY S, version_sort_value(VN), TT, priority_sort_value(PR) '
                            'LIMIT 1 '
                            'WHERE B type TT, B priority PR, B in_state S, B creation_date CD, B done_in V?, V num VN, B concerns P, P eid %s'
                            % self.ip1eid)
        rset.rows[0][4] = 'STATE'
        self.assertEqual(rset.rows, [[self.ip1t1eid, u'bug', timedelta(0), u'normal', 'STATE', self.ip1v1eid]])

    def test_nonregr8(self):
        self.execute('Any SN WHERE X has_text "toto", X in_state S, S name SN, X is IN (Project, Version, Transition)')

    def test_nonregr9(self):
        self.execute('DISTINCT Any AD,AE ORDERBY AE WHERE NOT S depends_on O, S eid %(x)s, O is Version, O in_state AD, AD name AE, AD modification_date AF',
                     {'x': self.ip1v1eid})


repo2, cnx2, repo3, cnx3, eids = ms_test_init(ThreeSourcesTC.datadir)
globals().update(eids)

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

from datetime import timedelta
from cubicweb import devtools # needed to ensure cubes.tracker is importable

from cubes.tracker.testutils import BaseMSTC, ms_test_init

def setUpModule(*args):
    global repo2, cnx2, repo3, cnx3
    repo2, cnx2, repo3, cnx3, eids = ms_test_init(ThreeSourcesTC.datadir)

def tearDownModule(*args):
    cnx2.close()
    repo2.shutdown()
    cnx3.close()
    repo3.shutdown()


class ThreeSourcesTC(BaseMSTC):
    def test_projects_interested_in(self):
        rset = self.execute('Any P,N WHERE P name N, X interested_in P, X eid %(x)s', {'x': self.session.user.eid})
        self.assertEqual(len(rset), 3)

    def test_nonregr2(self):
        self.execute('INSERT Card X: X title "test1", X test_case_of P WHERE P eid %(x)s', {'x': self.ip1eid})
        self.execute('INSERT Card X: X title "test2", X test_case_for T WHERE T eid %(x)s', {'x': self.ip1t1eid})
        self.commit()
        # test we can a change a ticket state (and implicitly its version'state by commiting
        self.fire_transition(self.ip1t1eid, 'start')
        self.commit()
        ip1v1 = self.execute('Any X WHERE X eid %(x)s', {'x': self.ip1v1eid}).get_entity(0, 0)
        self.assertEqual(ip1v1.cw_adapt_to('IWorkflowable').state, 'dev')

    def test_nonregr6(self):
        # XXX monkey patch of sqlgenerator needed since sqlite needs distinct
        # queries for has_text
        for repo in (self.repo, repo2, repo3):
            sqlgen = repo.system_source._rql_sqlgen
            sqlgen.union_sql = sqlgen._SQLGenerator__union_sql
        try:
            rset = self.execute('Any E,F ORDERBY F WHERE X has_text %(text)s, X in_state E, E name F',
                                {'text': 'extern'})
            self.assertEqual(len(rset), 2)
            rset = self.execute('Any E,F ORDERBY F WHERE X has_text %(text)s, X in_state E, E name F',
                                {'text': 'intern'})
            self.assertEqual(len(rset), 3)
            rset = self.execute('Any E,F ORDERBY F WHERE X has_text %(text)s, X in_state E, E name F',
                                {'text': 'project'})
            # 3 projects in two external sources, 3 projects + 2 tickets in internal source
            self.assertEqual(len(rset), 8)
            self.assertEqual(set(sn for s, sn in rset), set(('active development', 'open')))
        finally:
            for repo in (self.repo, repo2, repo3):
                sqlgen = repo.system_source._rql_sqlgen
                sqlgen.union_sql = sqlgen.has_text_need_distinct_union_sql

    def test_nonregr7(self):
        rset = self.execute('Any B,TT,NOW - CD,PR,S,C,V,group_concat(TN) '
                            'GROUPBY B,TT,CD,PR,S,C,V,VN '
                            'ORDERBY S, version_sort_value(VN), TT, priority_sort_value(PR) '
                            'LIMIT 1 '
                            'WHERE B type TT, B priority PR, B in_state S, B creation_date CD, B load C, T? tags B, T name TN, B done_in V?, V num VN, B concerns P, P eid %s'
                            % self.ip1eid)
        rset.rows[0][4] = 'STATE'
        self.assertEqual(rset.rows, [[self.ip1t1eid, u'bug', timedelta(0), u'normal', 'STATE', None, self.ip1v1eid, u'']])

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

"""functional tests for default forge security configuration"""
from cubicweb import Binary, Unauthorized
from cubicweb import devtools # necessary to import properly from cubes
from cubes.tracker.testutils import create_ticket_rql
from cubes.forge.testutils import ForgeSecurityTC

class ForgeSecurityTC(ForgeSecurityTC):

    def test_base_security(self):
        # staff users shouldn'- be able to insert/update project,extproject,license
        # but not "standard" users
        cnx = self.mylogin('staffuser')
        cu = cnx.cursor()
        # staff user insert
        cu.execute('INSERT ExtProject X: X name "myprojet"')
        cnx.commit() # OK
        cu.execute('INSERT License X: X name "mylicense"')
        self.assertRaises(Unauthorized, cnx.commit)
        # staff user update projects he doesn't own
        try:
            cu.execute('SET X name "mycubicweb" WHERE X is ExtProject, X name "projet externe"')
            cnx.commit() # OK
        finally: # manual rollback
            cu.execute('SET X name "projet externe" WHERE X is ExtProject, X name "mycubicweb"')
            cnx.commit() # OK
        cu.execute('SET X name "license1" WHERE X is License, X name "license"')
        self.assertRaises(Unauthorized, cnx.commit)
        cnx.rollback()
        cnx = self.mylogin('stduser')
        cu = cnx.cursor()
        # standard user create
        cu.execute('INSERT ExtProject X: X name "mystdprojet"')
        self.assertRaises(Unauthorized, cnx.commit)
        cu.execute('INSERT License X: X name "mystdlicense"')
        self.assertRaises(Unauthorized, cnx.commit)
        cnx.rollback()
        # licenses are public
        self.assert_(len(cu.execute('Any X WHERE X is License')) >= 1)
        # standard user try to update
        cu.execute('SET X name "projet externe renamed" WHERE X is ExtProject, X name "projet externe"')
        self.assertRaises(Unauthorized, cnx.commit)
        cu.execute('SET X name "license renamed" WHERE X is License, X name "license"')
        self.assertRaises(Unauthorized, cnx.commit)
        cnx.rollback()

    def _test_ticket_with_cubicweb_local_role(self, cnx):
        # cubicweb client/developper user attach something to a ticket
        cu = cnx.cursor()
        ticket = cu.execute(*create_ticket_rql('a ticket', 'cubicweb')).get_entity(0, 0)
        cnx.commit() # OK
        # and add file or image attachment
        cu.execute('INSERT File X: X data %(data)s, X data_name %(name)s, T attachment X WHERE T eid %(t)s',
                   {'data': Binary('hop'), 'name': u'hop.txt', 't': ticket.eid})
        cnx.commit() # OK
        cu.execute('INSERT File X: X data %(data)s, X data_name %(name)s, T attachment X WHERE T eid %(t)s',
                   {'data': Binary('hop'), 'name': u'hop.png', 't': ticket.eid})
        cnx.commit() # OK
        self.assertEqual(len(ticket.attachment), 2)

    def test_ticket_developper_security(self):
        # cubicweb developer user submit ticket
        cnx = self.mylogin('prj1developer')
        self._test_ticket_with_cubicweb_local_role(cnx)

    def test_ticket_client_security(self):
        # cubicweb client user submit ticket
        cnx = self.mylogin('prj1client')
        self._test_ticket_with_cubicweb_local_role(cnx)


    def test_ticket_workflow(self):
        b = self.create_ticket('a ticket').get_entity(0, 0)
        self.commit() # to set initial state properly
        self.assertEqual(b.cw_adapt_to('IWorkflowable').state, 'open')
        # only project's developer or user in the staff group can pass the wait for feedback transition
        self._test_tr_fail('stduser', b.eid, 'wait for feedback')
        self._test_tr_fail('prj1client', b.eid, 'wait for feedback')
        self._test_tr_success('prj1developer', b.eid, 'wait for feedback')
        # project's client, developer or user in the staff group can pass the
        # got feedback transition. Got feedback is a 'go back' transition
        self._test_tr_fail('stduser', b.eid, 'got feedback')
        self._test_tr_success('prj1client', b.eid, 'got feedback')
        #self._test_tr_success('staffuser', b.eid, 'got feedback')
        self.assertEqual(b.cw_adapt_to('IWorkflowable').state, 'open')
        # only staff/developer can pass the start transition
        self._test_tr_fail('stduser', b.eid, 'start')
        self._test_tr_fail('prj1client', b.eid, 'start')
        self._test_tr_success('prj1developer', b.eid, 'start')
        #self._test_tr_success('staffuser', b.eid, 'start')
        # project's client, developer or user in the staff group can pass the
        # got feedback transition. Got feedback is a 'go back' transition
        self._test_tr_success('staffuser', b.eid, 'wait for feedback')
        self._test_tr_success('prj1developer', b.eid, 'got feedback')
        b.cw_clear_all_caches()
        self.assertEqual(b.cw_adapt_to('IWorkflowable').state, 'in-progress')
        # staff/cubicweb developer can modify tickets even once no more in the open state
        cnx = self.mylogin('staffuser')
        cu = cnx.cursor()
        cu.execute('SET X description "bla" WHERE X eid %(x)s', {'x': b.eid})
        cnx.commit() # OK
        cnx = self.mylogin('prj1developer')
        cu = cnx.cursor()
        cu.execute('SET X description "bla bla" WHERE X eid %(x)s', {'x': b.eid})
        cnx.commit() # OK
        # though client can't, even their own tickets
        cnx = self.mylogin('prj1client')
        cu = cnx.cursor()
        cu.execute('SET X description "bla bla bla" WHERE X eid %(x)s', {'x': b.eid})
        self.assertRaises(Unauthorized, cnx.commit)
        tceid = cu.execute(*create_ticket_rql('a ticket', 'cubicweb'))[0][0]
        cnx.commit() # ok
        self._test_tr_success('staffuser', tceid, 'start')
        cnx = self.mylogin('prj1client')
        cu = cnx.cursor()
        cu.execute('SET X description "bla" WHERE X eid %(x)s', {'x': tceid})
        self.assertRaises(Unauthorized, cnx.commit)
        cnx.rollback()
        # only staff/developer can pass the done transition
        self._test_tr_fail('stduser', b.eid, 'done')
        self._test_tr_fail('prj1client', b.eid, 'done')
        self._test_tr_success('prj1developer', b.eid, 'done')
        # only staff/developer can pass the done transition XXX actually done automatically on version publishing
        self._test_tr_fail('stduser', b.eid, 'ask validation')
        self._test_tr_fail('prj1client', b.eid, 'ask validation')
        self._test_tr_success('prj1developer', b.eid, 'ask validation')
        #self._test_tr_success('staffuser', b.eid, 'done')
        # only staff/client can pass the resolve transition (though clients should,
        # use jplextranet for that
        self._test_tr_fail('prj1developer', b.eid, 'resolve')
        self._test_tr_success('prj1client', b.eid, 'resolve')
        #self._test_tr_success('staffuser', b.eid, 'resolve')
        # managers can do what they want, even going to a state without existing transition...
        b.cw_adapt_to('IWorkflowable').change_state('validation pending')
        b._cw.cnx.commit()
        # only staff/client can pass the reopen transition
        self._test_tr_fail('stduser', b.eid, 'refuse validation')
        self._test_tr_fail('prj1developer', b.eid, 'refuse validation')
        self._test_tr_success('prj1client', b.eid, 'refuse validation')
        b.cw_adapt_to('IWorkflowable').change_state('open')
        b._cw.cnx.commit()
        cnx = self.mylogin('prj1developer')
        # only staff/developer can pass the reject transition
        self._test_tr_fail('prj1client', b.eid, 'reject')
        self._test_tr_success('prj1developer', b.eid, 'reject')
        # staff/developer/client can pass the deprecate transition
        b.cw_adapt_to('IWorkflowable').change_state('open')
        b._cw.cnx.commit()
        self._test_tr_fail('stduser', b.eid, 'deprecate')
        self._test_tr_success('prj1developer', b.eid, 'deprecate')
        b.cw_adapt_to('IWorkflowable').change_state('open')
        b._cw.cnx.commit()
        self._test_tr_success('prj1client', b.eid, 'deprecate')

    def test_version_security(self):
        # cubicweb client add a version
        cnx = self.mylogin('prj1client')
        self.create_version('3.6')
        cnx.commit()

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

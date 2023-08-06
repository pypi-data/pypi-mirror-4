"""forge test application"""

from cubicweb.devtools.testlib import AutomaticWebTest
# from cubicweb.devtools.testlib import vreg_instrumentize, print_untested_objects


class AutomaticWebTest(AutomaticWebTest):
    no_auto_populate = ('TestInstance',)
    ignored_relations = set(('nosy_list',))

    def post_populate(self, cursor):
        self.commit()
        for version in cursor.execute('Version X').entities():
            version.cw_adapt_to('IWorkflowable').change_state('published')

def setUpModule(*args):
    #XXX DOESNT WORK vreg_instrumentize(AutomaticWebTest)
    pass

def tearDownModule(*args):
    #if not options.exitfirst or not (results.errors or results.failures):
    #    print_untested_objects(AutomaticWebTest)
    pass

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

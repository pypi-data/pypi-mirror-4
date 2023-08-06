"""Forge unit tests"""
from __future__ import with_statement

from datetime import datetime, timedelta

from PIL import Image

from logilab.common.testlib import unittest_main, SkipTest

from cubicweb.devtools import ApptestConfiguration
from cubicweb.devtools.testlib import AutoPopulateTest

from cubicweb import ValidationError, Unauthorized, Binary
from cubicweb import NoSelectableObject
from cubicweb.web.views import actions, workflow, idownloadable

from cubes.tracker.testutils import TrackerBaseTC
from cubes.tracker.views import ticket, document
from cubes.comment import views as commentactions
from cubes.forge.views import project as myproject, boxes
from cubes.nosylist import views as nosylist

ONEDAY = timedelta(1)

class ProjectTC(TrackerBaseTC):
    """Project"""

    def test_followup_wf(self):
        req = self.request()
        ticket = self.execute('INSERT Ticket X: X title "parent", X concerns P, X load 1 '
                              'WHERE P is Project').get_entity(0, 0)
        self.commit()
        iworkflowable = ticket.cw_adapt_to('IWorkflowable')
        for tr, state in [('done', 'done'), 
                          ('ask validation', 'validation pending'),
                          ('refuse validation', 'not validated')]:
            iworkflowable.fire_transition(tr)
            self.commit()
            ticket.cw_clear_all_caches()
            self.assertEqual(iworkflowable.state, state)

    def test_download_box(self):
        req = self.request()
        rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
        self.assertRaises(NoSelectableObject,
                          self.vreg['ctxcomponents'].select, 'download_box', req, rset=rset)
        self.execute('SET X downloadurl "ftp://ftp.logilab.org/pub/cubicweb/" WHERE X is Project')
        req = self.request()
        rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
        self.assertRaises(NoSelectableObject,
                          self.vreg['ctxcomponents'].select, 'download_box', req, rset=rset)
        v = self.create_version('0.0.0').get_entity(0, 0)
        self.commit()
        req = self.request()
        rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
        self.assertRaises(NoSelectableObject,
                          self.vreg['ctxcomponents'].select, 'download_box', req, rset=rset)
        v.cw_adapt_to('IWorkflowable').change_state('published')
        req = self.request()
        rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
        self.assertIsInstance(self.vreg['ctxcomponents'].select('download_box', req, rset=rset),
                              boxes.ProjectDownloadBox)
        self.commit()
        self.login('anon')
        req = self.request()
        rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
        self.assertIsInstance(self.vreg['ctxcomponents'].select('download_box', req, rset=rset),
                              boxes.ProjectDownloadBox)

    def test_possible_actions(self):
        req = self.request()
        # manager user, in dev project
        rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
        self.assertListEqual(self.pactions(req, rset),
                             [('workflow', workflow.WorkflowActions),
                              ('edit', actions.ModifyAction),
                              ('managepermission', actions.ManagePermissionsAction),
                              ('addrelated', actions.AddRelatedActions),
                              ('delete', actions.DeleteAction),
                              ('copy', actions.CopyAction),
                              ('actionsbox_notifications_mgmt', nosylist.INosyListManageNotificationsAction),
                              ('addticket', myproject.ProjectAddTicket),
                              ('addversion', myproject.ProjectAddVersion),
                              ('adddocumentationcard', myproject.ProjectAddDocumentationCard),
                              ('adddocumentationfile', myproject.ProjectAddDocumentationFile),
                              ('addscreenshot', myproject.ProjectAddScreenshot),
                              ('addtestcard', myproject.ProjectAddTestCard),
                              ('addsubproject', myproject.ProjectAddSubProject),
                              ('pvrestexport', document.ProjectVersionExportAction),
                              ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [])
        wf = self.cubicweb.cw_adapt_to('IWorkflowable').current_workflow
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                             [(u'temporarily stop development', u'http://testing.fr/cubicweb/project/cubicweb?treid=%s&vid=statuschange' %
                               wf.transition_by_name('temporarily stop development').eid),
                              (u'stop maintainance', u'http://testing.fr/cubicweb/project/cubicweb?treid=%s&vid=statuschange' %
                               wf.transition_by_name('stop maintainance').eid),
                              (u'project moved', u'http://testing.fr/cubicweb/project/cubicweb?treid=%s&vid=statuschange' %
                               wf.transition_by_name('project moved').eid),
                              (u'view workflow', u'http://testing.fr/cubicweb/workflow/%s'  % wf.eid)
                               ])
        # logilab user
        self.create_user(self.session, 'logilabien', ('staff', 'users'))
        self.login('logilabien')
        req = self.request()
        rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
        self.assertListEqual(self.pactions(req, rset),
                             [('workflow', workflow.WorkflowActions),
                              ('edit', actions.ModifyAction),
                              ('addrelated', actions.AddRelatedActions),
                              ('copy', actions.CopyAction),
                              ('addticket', myproject.ProjectAddTicket),
                              ('addversion', myproject.ProjectAddVersion),
                              ('adddocumentationcard', myproject.ProjectAddDocumentationCard),
                              ('adddocumentationfile', myproject.ProjectAddDocumentationFile),
                              ('addscreenshot', myproject.ProjectAddScreenshot),
                              ('addtestcard', myproject.ProjectAddTestCard),
                              ('addsubproject', myproject.ProjectAddSubProject),
                              ('pvrestexport', document.ProjectVersionExportAction),
                              ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                             [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                             [(u'temporarily stop development', u'http://testing.fr/cubicweb/project/cubicweb?treid=%s&vid=statuschange' %
                               wf.transition_by_name('temporarily stop development').eid),
                              (u'stop maintainance', u'http://testing.fr/cubicweb/project/cubicweb?treid=%s&vid=statuschange' %
                               wf.transition_by_name('stop maintainance').eid),
                              (u'project moved', u'http://testing.fr/cubicweb/project/cubicweb?treid=%s&vid=statuschange' %
                               wf.transition_by_name('project moved').eid),
                              (u'view workflow', u'http://testing.fr/cubicweb/workflow/%s'  % wf.eid)
                              ])
        # guest user
        self.login('anon')
        req = self.request()
        rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
        self.assertListEqual(self.pactions(req, rset),
                             [('workflow', workflow.WorkflowActions),
                              ('addrelated', actions.AddRelatedActions),
                              ('pvrestexport', document.ProjectVersionExportAction),
                              ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                             [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                             [])
        # std user, in dev project
        self.restore_connection()
        self.create_user(self.session, 'toto')
        self.login('toto')
        req = self.request()
        rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
        self.assertListEqual(self.pactions(req, rset),
                             [('workflow', workflow.WorkflowActions),
                              ('addrelated', actions.AddRelatedActions),
                              ('pvrestexport', document.ProjectVersionExportAction),
                              ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                             [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                             [])
        # std user with perm, in dev project
        self.restore_connection()# use the admin connection to create and link a permission
        self.grant_permission(self.session, self.cubicweb, 'users', 'developer',
                              'soumettre sur cubicweb')
        # commit before opening a new connection
        self.commit()
        self.login('toto')
        req = self.request()
        rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
        self.assertListEqual(self.pactions(req, rset),
                             [('workflow', workflow.WorkflowActions),
                              ('edit', actions.ModifyAction),
                              ('addrelated', actions.AddRelatedActions),
                              ('addticket', myproject.ProjectAddTicket),
                              ('adddocumentationcard', myproject.ProjectAddDocumentationCard),
                              ('adddocumentationfile', myproject.ProjectAddDocumentationFile),
                              ('addscreenshot', myproject.ProjectAddScreenshot),
                              ('addtestcard', myproject.ProjectAddTestCard),
                              ('pvrestexport', document.ProjectVersionExportAction),
                              ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                             [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                             [])
        # std user with client perm, in dev project
        self.restore_connection()# use the admin connection to create and link a permission
        self.grant_permission(self.session, self.cubicweb, 'users', 'client',
                              'nouvelle version')
        self.commit()
        # commit before opening a new connection
        self.login('toto')
        req = self.request()
        rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
        rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
        self.assertListEqual(self.pactions(req, rset),
                             [('workflow', workflow.WorkflowActions),
                              ('edit', actions.ModifyAction),
                              ('addrelated', actions.AddRelatedActions),
                              ('addticket', myproject.ProjectAddTicket),
                              ('addversion', myproject.ProjectAddVersion),
                              ('adddocumentationcard', myproject.ProjectAddDocumentationCard),
                              ('adddocumentationfile', myproject.ProjectAddDocumentationFile),
                              ('addscreenshot', myproject.ProjectAddScreenshot),
                              ('addtestcard', myproject.ProjectAddTestCard),
                              ('pvrestexport', document.ProjectVersionExportAction),
                              ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                             [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                             [])
        # manager user, moved project
        self.restore_connection()
        self.cubicweb.cw_adapt_to('IWorkflowable').fire_transition('project moved')
        self.commit()
        req = self.request()
        rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
        self.assertListEqual(self.pactions(req, rset),
                             [('workflow', workflow.WorkflowActions),
                              ('edit', actions.ModifyAction),
                              ('managepermission', actions.ManagePermissionsAction),
                              ('addrelated', actions.AddRelatedActions),
                              ('delete', actions.DeleteAction),
                              ('copy', actions.CopyAction),
                              ('actionsbox_notifications_mgmt', nosylist.INosyListManageNotificationsAction),
                              ('pvrestexport', document.ProjectVersionExportAction),
                              ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                             [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                             [(u'view history', u'http://testing.fr/cubicweb/project/cubicweb?vid=wfhistory')])

    def test_doap(self):
        self.create_version('0.1.0')
        self.execute('INSERT MailingList M: M name "python-projects", '
                     'M email_address "python-projects@logilab.org", M mailinglist_of P '
                     'WHERE P is Project')[0]
        self.cubicweb.view('doap')

    def test_creator_interested_in(self):
        self.assertEqual(len(self.cubicweb.reverse_interested_in), 1)

    def test_add_icon(self):
        """ Add an icon to the project, check its new size and format. """
        # add an icon `tux.png` of size 200 x 232
        img = Binary.from_file(self.datapath('tux.png'))
        self.cubicweb.set_attributes(icon=img)
        self.commit()
        self.cubicweb.cw_clear_all_caches()
        # read the icon image, check its size and format
        icon = Image.open(self.cubicweb.icon)
        self.assertEqual(50, max(icon.size))
        self.assertEqual('image/png', self.cubicweb.icon_format)


class VersionTC(TrackerBaseTC):
    """Version"""
    def setup_database(self):
        super(VersionTC, self).setup_database()
        self.v = self.create_version(u'0.0.0').get_entity(0, 0)
        #self.t1 = self.create_ticket(u"story1", u'0.0.0').get_entity(0, 0)

    def test_download_box(self):
        req = self.request()
        rset = req.execute('Any X WHERE X is Version, X num "0.0.0"')
        self.assertRaises(NoSelectableObject,
                          self.vreg['ctxcomponents'].select, 'download_box', req, rset=rset)
        self.execute('SET X downloadurl "ftp://ftp.logilab.org/pub/cubicweb/" WHERE X is Project')
        req = self.request()
        rset = req.execute('Any X WHERE X is Version, X num "0.0.0"')
        self.assertRaises(NoSelectableObject,
                          self.vreg['ctxcomponents'].select, 'download_box', req, rset=rset)
        self.v.cw_adapt_to('IWorkflowable').change_state('published')
        req = self.request()
        rset = req.execute('Any X WHERE X is Version, X num "0.0.0"')
        self.assertIsInstance(self.vreg['ctxcomponents'].select('download_box', req, rset=rset),
                              idownloadable.DownloadBox)
        self.commit()
        self.login('anon')
        req = self.request()
        rset = req.execute('Any X WHERE X is Version, X num "0.0.0"')
        self.assertIsInstance(self.vreg['ctxcomponents'].select('download_box', req, rset=rset),
                              idownloadable.DownloadBox)

class TicketTC(TrackerBaseTC):
    """Ticket"""

    def setup_database(self):
        super(TicketTC, self).setup_database()
        self.v = self.create_version(u'0.0.0').get_entity(0, 0)
        self.t1 = self.create_ticket(u"story1").get_entity(0, 0)

    def test_creator_interested_in(self):
        t = self.create_ticket('pouet').get_entity(0, 0)
        self.assertEqual(len(t.reverse_interested_in), 1)

    def test_load_after_state_changed_deprecated(self):
        self.t1.set_attributes(load=2)
        self.t1.cw_adapt_to('IWorkflowable').change_state('deprecated')
        self.commit()
        self.t1.cw_attr_cache.pop('load', None)
        self.assertEqual(self.t1.load, 0)

    def test_load_after_state_changed_rejected(self):
        self.t1.set_attributes(load=2)
        self.t1.cw_adapt_to('IWorkflowable').change_state('rejected')
        self.commit()
        self.t1.cw_attr_cache.pop('load', None)
        self.assertEqual(self.t1.load, 0)

    def test_auto_set_load_left_1(self):
        t = self.execute('INSERT Ticket X: X title "story1", X concerns P, X load 1 '
                         'WHERE P is Project').get_entity(0, 0)
        self.assertEqual(t.load_left, 1.0)

    def test_auto_set_load_left_2(self):
        self.execute('SET X load 1 WHERE X eid %(x)s', {'x': self.t1.eid})
        self.t1.cw_attr_cache.pop('load_left', None)
        self.assertEqual(self.t1.load_left, 1)
        self.execute('SET X load 2 WHERE X eid %(x)s', {'x': self.t1.eid})
        self.t1.cw_attr_cache.pop('load_left', None)
        self.assertEqual(self.t1.load_left, 1)

    def test_modification_date_after_comment_added(self):
        olddate = datetime.today() - ONEDAY
        self.t1.set_attributes(modification_date=olddate)
        ceid = self.execute('INSERT Comment C: C content "A commment", C comments X '
                            'WHERE X eid %(x)s', {'x': self.t1.eid})[0][0]
        self.commit()
        self.assertModificationDateGreater(self.t1, olddate)
        self.t1.set_attributes(modification_date=olddate)
        ceid2 = self.execute('INSERT Comment C: C content "A commment", C comments X '
                             'WHERE X eid %(x)s', {'x': ceid})[0][0]
        self.commit()
        self.assertModificationDateGreater(self.t1, olddate)
        self.t1.set_attributes(modification_date=olddate)
        self.execute('INSERT Comment C: C content "A commment", C comments X '
                     'WHERE X eid %(x)s', {'x': ceid2})
        self.commit()
        self.assertModificationDateGreater(self.t1, olddate)

    def test_possible_actions(self):
        req = self.request()
        rset = req.execute('Any X WHERE X is Ticket')
        _ticket = rset.get_entity(0, 0)
        teid = rset[0][0]
        self.assertListEqual(self.pactions(req, rset),
                             [('workflow', workflow.WorkflowActions),
                              ('edit', actions.ModifyAction),
                              ('managepermission', actions.ManagePermissionsAction),
                              ('addrelated', actions.AddRelatedActions),
                              ('delete', actions.DeleteAction),
                              ('copy', actions.CopyAction),
                              ('actionsbox_notifications_mgmt', nosylist.INosyListManageNotificationsAction),
                              ('movetonext', ticket.TicketMoveToNextVersionActions),
                              ('reply_comment', commentactions.AddCommentAction)])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [('add Ticket attachment File subject',
                                'http://testing.fr/cubicweb/add/File?__linkto=attachment%%3A%s%%3Aobject&__redirectpath=ticket%%2F%s&__redirectvid='
                                % (teid, teid)),
                               ('add Card test_case_for Ticket object',
                                'http://testing.fr/cubicweb/add/Card?__linkto=test_case_for%%3A%s%%3Asubject&__redirectpath=ticket%%2F%s&__redirectvid='
                                % (teid, teid))])
        wf = self.t1.cw_adapt_to('IWorkflowable').current_workflow
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                             [(u'start', u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                               (self.t1.eid, wf.transition_by_name('start').eid)),
                              (u'reject', u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                               (self.t1.eid, wf.transition_by_name('reject').eid)),
                              (u'done', u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                               (self.t1.eid, wf.transition_by_name('done').eid)),
                              (u'deprecate', u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                               (self.t1.eid, wf.transition_by_name('deprecate').eid)),
                              (u'wait for feedback', u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                               (self.t1.eid, wf.transition_by_name('wait for feedback').eid)),
                              (u'view workflow', u'http://testing.fr/cubicweb/workflow/%s'  % wf.eid)])
        movetonext = self.action_submenu(req, rset, 'movetonext')
        self.assertEqual(len(movetonext), 1)
        self.assertEqual(movetonext[0][0], '0.0.0')
        self.login('anon')
        req = self.request()
        rset = req.execute('Any X WHERE X is Ticket')
        self.assertListEqual(self.pactions(req, rset),
                             [('workflow', workflow.WorkflowActions),
                              ('addrelated', actions.AddRelatedActions),
                              ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                             [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                             [])
        self.restore_connection()
        req = self.request()
        self.t1.cw_adapt_to('IWorkflowable').fire_transition('done')
        self.commit()
        rset = req.execute('Any X WHERE X is Ticket')
        self.assertListEqual(self.pactions(req, rset),
                             [('workflow', workflow.WorkflowActions),
                              ('edit', actions.ModifyAction),
                              ('managepermission', actions.ManagePermissionsAction),
                              ('addrelated', actions.AddRelatedActions),
                              ('delete', actions.DeleteAction),
                              ('copy', actions.CopyAction),
                              ('actionsbox_notifications_mgmt', nosylist.INosyListManageNotificationsAction),
                              ('reply_comment', commentactions.AddCommentAction)])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                              [('add Ticket attachment File subject',
                                'http://testing.fr/cubicweb/add/File?__linkto=attachment%%3A%s%%3Aobject&__redirectpath=ticket%%2F%s&__redirectvid='
                                % (teid, teid)),
                               ('add Card test_case_for Ticket object',
                                'http://testing.fr/cubicweb/add/Card?__linkto=test_case_for%%3A%s%%3Asubject&__redirectpath=ticket%%2F%s&__redirectvid='
                                % (teid, teid))])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                             [(u'ask validation', u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                               (self.t1.eid, wf.transition_by_name('ask validation').eid)),
                              (u'reopen', u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                               (self.t1.eid, wf.transition_by_name('reopen').eid)),
                              (u'view workflow', u'http://testing.fr/cubicweb/workflow/%s'  % wf.eid),
                              (u'view history', u'http://testing.fr/cubicweb/ticket/%s?vid=wfhistory' % self.t1.eid)])
        self.login('anon')
        req = self.request()
        rset = req.execute('Any X WHERE X is Ticket')
        self.assertListEqual(self.pactions(req, rset),
                             [('workflow', workflow.WorkflowActions),
                              ('addrelated', actions.AddRelatedActions),
                              ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                             [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                             [(u'view history', u'http://testing.fr/cubicweb/ticket/%s?vid=wfhistory' % self.t1.eid)])
        self.restore_connection()
        self.t1.cw_adapt_to('IWorkflowable').fire_transition('ask validation')
        req = self.request()
        rset = req.execute('Any X WHERE X is Ticket')
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                             [(u'resolve', u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                               (self.t1.eid, wf.transition_by_name('resolve').eid)),
                              (u'refuse validation', u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                               (self.t1.eid, wf.transition_by_name('refuse validation').eid)),
                              (u'view workflow', u'http://testing.fr/cubicweb/workflow/%s'  % wf.eid),
                              (u'view history', u'http://testing.fr/cubicweb/ticket/%s?vid=wfhistory' % self.t1.eid)])
        self.t1.cw_adapt_to('IWorkflowable').fire_transition('resolve')
        self.commit()
        req = self.request()
        rset = req.execute('Any X WHERE X is Ticket')
        self.assertListEqual(self.pactions(req, rset),
                             [('workflow', workflow.WorkflowActions),
                              ('edit', actions.ModifyAction),
                              ('managepermission', actions.ManagePermissionsAction),
                              ('addrelated', actions.AddRelatedActions),
                              ('delete', actions.DeleteAction),
                              ('copy', actions.CopyAction),
                              ('actionsbox_notifications_mgmt', nosylist.INosyListManageNotificationsAction),
                              ('reply_comment', commentactions.AddCommentAction)])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                             [('add Ticket attachment File subject',
                               'http://testing.fr/cubicweb/add/File?__linkto=attachment%%3A%s%%3Aobject&__redirectpath=ticket%%2F%s&__redirectvid='
                               % (teid, teid)),
                              ('add Card test_case_for Ticket object',
                               'http://testing.fr/cubicweb/add/Card?__linkto=test_case_for%%3A%s%%3Asubject&__redirectpath=ticket%%2F%s&__redirectvid='
                               % (teid, teid))])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                             [(u'view history', u'http://testing.fr/cubicweb/ticket/%s?vid=wfhistory' % self.t1.eid)])
        self.login('anon')
        req = self.request()
        rset = req.execute('Any X WHERE X is Ticket')
        self.assertListEqual(self.pactions(req, rset),
                             [('workflow', workflow.WorkflowActions),
                              ('addrelated', actions.AddRelatedActions),
                              ])
        self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                             [])
        self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                             [(u'view history', u'http://testing.fr/cubicweb/ticket/%s?vid=wfhistory' % self.t1.eid)])

    def test_state_change_on_version_publishing(self):
        v2 = self.execute('INSERT Version V: V num "0.0.1", V version_of P '
                          'WHERE P is Project').get_entity(0, 0)
        self.t1.set_relations(done_in=v2)
        self.commit()
        t1iwf = self.t1.cw_adapt_to('IWorkflowable')
        t1iwf.fire_transition('done')
        self.t1.cw_clear_all_caches()
        self.assertEqual(t1iwf.state, 'done')
        self.commit()
        v2.cw_clear_all_caches()
        v2._cw = self.request()
        v2iwf = v2.cw_adapt_to('IWorkflowable')
        self.assertEqual(v2iwf.state, 'dev')
        v2.cw_clear_all_caches()
        v2iwf.change_state('published')
        self.commit()
        self.t1.cw_clear_all_caches()
        self.assertEqual(t1iwf.state, 'validation pending')

    def test_version_publishing_cant_change_ticket_state(self):
        self.execute('INSERT CWGroup X: X name "cubicwebdevelopers"')
        self.grant_permission(self.session, self.cubicweb, 'cubicwebdevelopers',
                              u'developer')
        self.create_user(self.session, 'prj1client', groups=('users', 'cubicwebdevelopers'))
        self.commit()
        self.t1.set_relations(done_in=self.v)
        # -  change ticket status
        t1iwf= self.t1.cw_adapt_to('IWorkflowable')
        t1iwf.fire_transition('done')
        self.t1.cw_clear_all_caches()
        self.v.cw_clear_all_caches()
        self.assertEqual(t1iwf.state, 'done')
        # -  Remove permission on the ticket for the clients
        self.execute('DELETE X require_permission P WHERE X eid %s' % self.t1.eid)
        self.commit()
        # - publish version as client
        self.login('prj1client')
        v2 =  self.execute('Any X WHERE X version_of P, P name "cubicweb", P is Project, X num "0.0.0"').get_entity(0, 0)
        t1 =  self.execute('Any X WHERE X in_state S, S name SN, X eid %s'% self.t1.eid).get_entity(0, 0)
        # - can't change ticket's state
        t1iwf= t1.cw_adapt_to('IWorkflowable')
        self.assertRaises(ValidationError, t1iwf.fire_transition, 'ask validation')
        self.rollback()
        v2.cw_adapt_to('IWorkflowable').fire_transition('publish')
        self.commit()
        # - verify that ticket on which permissions were revoked remains in state
        self.assertEqual(t1iwf.state, 'done')
        # only managers are enabled to move away ticket from a published version
        self.assertRaises(Unauthorized, self.execute,
                          'DELETE X done_in V WHERE X eid %(x)s', {'x': t1.eid})
        self.rollback()
        self.restore_connection()
        self.create_user(self.session, 'staffuser', groups=('users', 'staff',))
        with self.login('staffuser'):
            self.assertRaises(Unauthorized, self.execute,
                              'DELETE X done_in V WHERE X eid %(x)s', {'x': t1.eid})
            self.rollback()


class CommentTC(AutoPopulateTest):
    no_auto_populate = ('TestInstance',)
    ignored_relations = set(('nosy_list',))

    def test_comment_root(self):
        """comments in Forge require that a project property is defined on commentable object
        """
        self.auto_populate(1)
        rschema = self.schema.rschema('comments')
        for etype in rschema.objects():
            if etype == 'TestInstance':
                continue
            eid = self.execute('Any X LIMIT 1 WHERE X is %s' % etype)[0][0]
            comment = self.execute('INSERT Comment C: C content "a comment", C comments X WHERE X eid %(x)s',
                                  {'x': eid}).get_entity(0, 0)
            try:
                comment.project
            except AttributeError:
                self.fail('%s class does not implement the project property' % etype)


class FTITC(TrackerBaseTC):
    config = ApptestConfiguration('data', apphome=CommentTC.datadir,
                                  sourcefile='sources_fti')
    @classmethod
    def _init_repo(cls, *args, **kwargs):
        try:
            super(FTITC, cls)._init_repo(*args, **kwargs)
        except Exception, ex:
            # much probably on a wrong host
            raise SkipTest(ex)

    def test_entity_weight(self):
        comment = self.request().create_entity('Comment',
                                               content=u'cubicweb comment')
        ticket = self.request().create_entity('Ticket',
                                              title=u'bug in cubicweb',
                                              reverse_comments=comment,
                                              concerns=self.cubicweb)
        self.commit()
        self.assertEqual(self.request().execute('Any X ORDERBY FTIRANK(X) DESC WHERE X has_text "cubicweb"').rows,
                          [[self.cubicweb.eid], [ticket.eid], [comment.eid]])


if __name__ == '__main__':
    unittest_main()

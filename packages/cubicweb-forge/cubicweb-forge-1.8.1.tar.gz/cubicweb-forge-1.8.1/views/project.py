"""views for Project entities

:organization: Logilab
:copyright: 2006-2011 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.common.decorators import monkeypatch
from logilab.mtconverter import xml_escape

from cubicweb.predicates import one_line_rset, score_entity, is_instance
from cubicweb.view import EntityView
from cubicweb import tags
from cubicweb.web import uicfg, action
from cubicweb.web.views import (primary, tabs, baseviews, tableview,
                                idownloadable)

from cubes.testcard import views as testcard
from cubes.tracker.views import fixed_orderby_rql, project as tracker


tracker.ProjectStatsView.default_rql = (
    'Any P, PN WHERE P is Project, P name PN, '
    'P in_state S, S name "active development"')

idx = tracker.ProjectTicketsTable.columns.index('in_state')
tracker.ProjectTicketsTable.columns.insert(idx+1, 'load')
tracker.ProjectTicketsTable.columns.append('tags')
tracker.ProjectTicketsTable.column_renderers['tags'] = \
    tableview.RelationColRenderer(role='object')

tracker.ProjectTicketsTab.TICKET_DEFAULT_STATE_RESTR \
    = 'S name IN ("open","done","waiting feedback","in-progress","validation pending")'

@monkeypatch(tracker.ProjectTicketsTab)
def tickets_rql(self):
    # prefetch everything we can for optimization
    return ('Any T,TTI,TT,TP,TD,TDF,TCD,TMD,TL,S,SN,V,VN,U,UL %s WHERE '
            'T title TTI, T type TT, T priority TP, '
            'T description TD, T description_format TDF, '
            'T creation_date TCD, T modification_date TMD, '
            'T load TL,'
            'T in_state S, S name SN, '
            'T done_in V?, V num VN, '
            'T created_by U?, U login UL, '
            'T concerns P, P eid %%(x)s'
            % fixed_orderby_rql(self.SORT_DEFS))


# primary view and tabs ########################################################

class ExtProjectPrimaryView(primary.PrimaryView):
    __select__ = is_instance('ExtProject')
    show_attr_label = False

    def render_entity_title(self, entity):
        title = u'<a href="%s">%s</a>' % (xml_escape(entity.homepage),
                                          xml_escape(entity.name))
        self.w(u'<h1><span class="etype">%s</span> %s</h1>'
               % (entity.dc_type().capitalize(), title))

tracker.ProjectPrimaryView.tabs +=  [
    _('documentation_tab'), _('screenshots_tab')]


_pvs = uicfg.primaryview_section
_pvs.tag_attribute(('Project', 'downloadurl'), 'hidden')
_pvs.tag_subject_of(('Project', 'recommends', '*'), 'attributes')
_pvs.tag_object_of(('Project', 'recommends', '*'), 'hidden')
_pvs.tag_object_of(('*', 'license_of', 'Project'), 'attributes')
_pvs.tag_object_of(('*', 'mailinglist_of', 'Project'), 'attributes')
_pvs.tag_subject_of(('*', 'documented_by', '*'), 'hidden')

_pvdc = uicfg.primaryview_display_ctrl
for attr in ('homepage', 'downloadurl'):
    _pvdc.tag_attribute(('Project', attr), {'vid': 'urlattr'})
_pvdc.tag_attribute(('Project', 'icon'), {'showlabel': False})


# XXX cleanup or explain View/Tab duality

class ProjectDocumentationView(tabs.EntityRelationView):
    """display project's documentation"""
    __regid__ = title = _('projectdocumentation')
    __select__ = tabs.EntityRelationView.__select__ & is_instance('Project')
    rtype = 'documented_by'
    target = 'object'

class ProjectDocumentationTab(ProjectDocumentationView):
    __regid__ = 'documentation_tab'
    title = None # should not appears in possible views
    __select__ = ProjectDocumentationView.__select__ & one_line_rset()


class ProjectScreenshotsView(tabs.EntityRelationView):
    """display project's screenshots"""
    __regid__ = title = _('projectscreenshots')
    __select__ = tabs.EntityRelationView.__select__ & is_instance('Project')
    rtype = 'screenshot'
    target = 'object'
    vid = 'gallery'

class ProjectScreenshotsTab(ProjectScreenshotsView):
    __regid__ = 'screenshots_tab'
    __select__ = tabs.EntityRelationView.__select__ & is_instance('Project')
    title = None # should not appears in possible views

class ProjectListView(baseviews.SameETypeListView):
    __select__ = (baseviews.SameETypeListView.__select__ &
                  is_instance("Project"))
    def call(self, **kwargs):
        # sort by modification date
        self.cw_rset = self.cw_rset.sorted_rset(lambda e: e.cw_attr_cache['modification_date'],
                                                reverse=True)
        super(ProjectListView, self).call(**kwargs)

class ProjetListItemView(baseviews.SameETypeListItemView):
    __select__ = (baseviews.SameETypeListItemView.__select__ &
                  is_instance("Project"))

    def cell_call(self, row, col, **kwargs):
        self._cw.add_css('cubes.forge.css')
        entity = self.cw_rset.get_entity(row, col)
        title = xml_escape(entity.dc_title())
        updated = entity.cw_attr_cache['modification_date'].strftime('%F, %R')
        if entity.icon:
            icon = entity.absolute_url(vid='icon')
        else:
            icon = self._cw.data_url('project-icon.png')
        # project icon
        self.w(u'<div class="project-item">')
        self.w(u'<div class="iconwrapper"><img alt="%(title)s" src="%(icon)s"/></div>'
               % {'title': title, 'icon': xml_escape(icon)})
        self.w(u'<div class="textwrapper">')
        # project title, last update date and maybe summary
        self.w(u'<h3>')
        self.wview('oneline', entity.as_rset())
        self.w(u'</h3>')
        self.w(u'<div class="updated">')
        self.w(u'<p>')
        self.w(u'updated on: %s' % updated)
        self.w(u'</p>')
        self.w(u'</div>')
        if entity.summary:
            self.w(u'<div class="summary">')
            self.w(u'<p>')
            self.w(xml_escape(entity.summary))
            self.w(u'</p>')
            self.w(u'</div>')
        self.w(u'</div>')
        self.w(u'</div>')

class ProjectIconView(idownloadable.DownloadView):
    __regid__ = 'icon'
    __select__ = one_line_rset() & is_instance('Project')

    @property
    def content_type(self):
        entity = self.cw_rset.complete_entity(self.cw_row or 0, self.cw_col or 0)
        return entity.icon_format

    def set_request_content_type(self):
        EntityView.set_request_content_type(self)

    def call(self):
        entity = self.cw_rset.complete_entity(self.cw_row or 0, self.cw_col or 0)
        self.w(entity.icon.getvalue())


# secondary views ##############################################################

class ExtProjectOutOfContextView(baseviews.OutOfContextView):
    """project's out-of-context view display project's url and summary, which
    are not displayed in the one line / text views
    """
    __select__ = is_instance('ExtProject')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'&nbsp;')
        self.w(tags.a(entity.name, href=entity.absolute_url()))
        if getattr(entity, 'homepage', None):
            self.w(u'&nbsp;')
            self.w(tags.a(entity.homepage, href=entity.homepage))


class ProjectTextView(baseviews.TextView):
    __select__ = is_instance('Project')

    def cell_call(self, row, col):
        """text representation of a project"""
        entity = self.cw_rset.get_entity(row, col)
        self.w(entity.name)
        state = entity.cw_adapt_to('IWorkflowable').state
        if state != 'active development':
            self.w(u' [%s]' % self._cw._(state))


class ProjectOneLineView(baseviews.OneLineView):
    __select__ = is_instance('Project')

    def cell_call(self, row, col):
        """oneline representation of a project, including state information
        """
        entity = self.cw_rset.get_entity(row, col)
        iwf = entity.cw_adapt_to('IWorkflowable')
        if iwf.state != 'active development':
            title = 'project %(project)s in state %(state)s' % {
                'project': entity.name, 'state': iwf.printable_state}
            self.w(u'<em>%s</em>' % tags.a(entity.name, title=title,
                                           href=entity.absolute_url()))
        else:
            self.w(tags.a(entity.name, href=entity.absolute_url()))


class ProjectOutOfContextView(tracker.ProjectOutOfContextView):
    """project's secondary view display project's url, which is not
    displayed in the one line / text views
    """
    __select__ = is_instance('Project')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(tags.a(entity.name, href=entity.absolute_url()))
        if getattr(entity, 'homepage', None):
            self.w(u'&nbsp;')
            self.w(tags.a(entity.homepage, href=entity.homepage))
        # no summary on ext project
        if getattr(entity, 'summary', None):
            self.w(u'&nbsp;')
            self.w(xml_escape(entity.summary))


# Project actions #############################################################

class ProjectAddRelatedAction(action.LinkToEntityAction):
    __select__ = (action.LinkToEntityAction.__select__ & is_instance('Project')
                  & score_entity(lambda x: x.cw_adapt_to('IWorkflowable').state != 'moved'))

class ProjectAddTicket(ProjectAddRelatedAction):
    __regid__ = 'addticket'
    rtype = 'concerns'
    role = 'object'
    target_etype = 'Ticket'
    title = _('add Ticket concerns Project object')
    order = 110

class ProjectAddVersion(ProjectAddRelatedAction):
    __regid__ = 'addversion'
    rtype = 'version_of'
    role = 'object'
    target_etype = 'Version'
    title = _('add Version version_of Project object')
    order = 112

class ProjectAddDocumentationCard(ProjectAddRelatedAction):
    __regid__ = 'adddocumentationcard'
    rtype = 'documented_by'
    role = 'subject'
    target_etype = 'Card'
    title = _('add Project documented_by Card subject')
    order = 120

class ProjectAddDocumentationFile(ProjectAddRelatedAction):
    __regid__ = 'adddocumentationfile'
    rtype = 'documented_by'
    role = 'subject'
    target_etype = 'File'
    title = _('add Project documented_by File subject')
    order = 121

class ProjectAddScreenshot(ProjectAddRelatedAction):
    __regid__ = 'addscreenshot'
    rtype = 'screenshot'
    role = 'subject'
    target_etype = 'File'
    title = _('add Project screenshot File subject')
    order = 122

class ProjectAddSubProject(ProjectAddRelatedAction):
    __regid__ = 'addsubproject'
    rtype = 'subproject_of'
    role = 'object'
    target_etype = 'Project'
    title = _('add Project subproject_of Project object')
    order = 130


class ProjectAddTestCard(testcard.ProjectAddTestCard):
    __select__ = ProjectAddRelatedAction.__select__

# register messages generated for the form title until catalog generation is fixed
# some are missing because they are defined in tracker
_('creating Card (Project %(linkto)s) documented_by Card')
_('creating File (Project %(linkto)s) documented_by File')
_('creating File (Project %(linkto)s) screenshot File')

_abaa = uicfg.actionbox_appearsin_addmenu
for cls in ProjectAddRelatedAction.__subclasses__():
    if cls.role == 'object':
        _abaa.tag_object_of(('*', cls.rtype, 'Project'), False)
    else:
        _abaa.tag_subject_of(('Project', cls.rtype, '*'), False)

# del cls local identifier else ProjectAddVersion is referenced twice and it
# triggers a registration error
del cls

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__,
                      (ProjectOutOfContextView, ProjectAddTestCard))
    vreg.register_and_replace(ProjectOutOfContextView, tracker.ProjectOutOfContextView)
    vreg.register_and_replace(ProjectAddTestCard, testcard.ProjectAddTestCard)

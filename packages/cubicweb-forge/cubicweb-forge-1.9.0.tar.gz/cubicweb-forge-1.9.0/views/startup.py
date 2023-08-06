"""forge specific index view

:organization: Logilab
:copyright: 2006-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb.web.views import startup, tableview


class IndexView(startup.IndexView):
    title = _('Index')
    add_etype_links = ('Project',)

    upcoming_versions = ('Any X,D ORDERBY D DESC LIMIT 5 WHERE X is Version, X prevision_date D, '
                         'NOT X prevision_date NULL, X in_state S, S name "dev"')
    latest_releases = ('Any X,D ORDERBY D DESC LIMIT 5 WHERE X is Version, X publication_date D, '
                       'NOT X publication_date NULL, X in_state S, S name "published"')
    new_projects = 'Any P,S ORDERBY CD DESC LIMIT 5 WHERE P is Project, P summary S, P creation_date CD'

    def _header(self):
        self.whead(u'<link  rel="meta" type="application/rdf+xml" title="FOAF" '
                   u'href="%s"/>' % self._cw.build_url('foaf.rdf'))
        stitle = self._cw.property_value('ui.site-title')
        if stitle:
            self.w(u'<h1>%s</h1>' % self._cw.property_value('ui.site-title'))

    def _left_section(self):
        _ = self._cw._
        w = self.w
        user = self._cw.user
        rset = self._cw.execute('Card X WHERE X wikiid "index"')
        if not user.matching_groups('users'):
            w(u'<div>')
            if rset:
                self.wview('inlined', rset, row=0)
            w(u'</div>')
        else:
            self._cw.add_css('cubes.forge.css')
            w(u'<div class="quickLinks">')
            self.create_links()
            w(u'<div class="hr">&nbsp;</div>')
            # XXX sort
            # XXX bad title (there may be blogs in there...)
            w(u'<h5>%s</h5>' % _('Projects I\'m interested in'))
            w(u'<div>')
            w(u'<table width="100%"><tr><td>')
            projects = [proj for proj in user.interested_in
                        if ((proj.__regid__ == 'Project'
                             and proj.cw_adapt_to('IWorkflowable').state == 'active development')
                            or proj.__regid__ == 'Blog')]
            if len(projects) > 50:
                chcol = len(projects) // 2
            else:
                chcol = None # all projects in one column
            for i, project in enumerate(projects):
                w(u'%s<br/>' % project.view('incontext'))
                if i == chcol:
                    w(u'</td><td>')
            w(u'</td></tr></table>')
            w(u'<p><a href="%s">%s</a></p>' % (self._cw.build_url('project'),
                                               _('view all active projects')))
            w(u'</div>')
            if user.matching_groups('managers'):
                self.w(u'<div class="hr">&#160;</div>')
                if rset:
                    href = rset.get_entity(0, 0).absolute_url(vid='edition')
                    label = self._cw._('edit the index page')
                else:
                    href = self._cw.build_url('view', vid='creation', etype='Card', wikiid='index')
                    label = self._cw._('create an index page')
                self.w(u'<br/><a href="%s">%s</a>\n' % (xml_escape(href), label))
            w(u'</div>')

    def _right_section(self):
        user = self._cw.user; _ = self._cw._; w = self.w
        if not user.matching_groups('users'):
            w(u'<div>')
            w(u'<h2>%s</h2>\n' % self._cw._('Browse by category'))
            self._cw.vreg['views'].select('tree', self._cw).render(w=w, maxlevel=1)
            w(u'</div>')
        w(u'</td><td style="width: 50%;">')
        # projects the user is subscribed to
        if user.is_in_group('users'):
            rql = ('Any X, NOW - CD, P ORDERBY CD DESC LIMIT 5 WHERE U interested_in P, '
                   'U eid %(x)s, X concerns P, X creation_date CD')
            rset = self._cw.execute(rql, {'x': user.eid})
            self.wview('table', rset, 'null',
                       headers=[_(u'Recent tickets in my projects'), _(u'Date'),
                                _(u'Project')])
        # tickets
        if user.is_in_group('guests'):
            rql = 'Any X, NOW - CD, P ORDERBY CD DESC LIMIT 5 WHERE X concerns P, X creation_date CD'
            rset = self._cw.execute(rql)
        else:
            rql = ('Any X, NOW - CD, P ORDERBY CD DESC LIMIT 5 WHERE X concerns P, '
                   'X creation_date CD, NOT U interested_in P, U eid %(x)s')
            rset = self._cw.execute(rql, {'x': user.eid})
        self.wview('table', rset, 'null',
                   headers=[_(u'Recent tickets'), _(u'Date'),_(u'Project')])
        # upcoming versions
        rset = self._cw.execute(self.upcoming_versions)
        self.wview('ooctable', rset, 'null',
                   headers=[_(u'Upcoming versions'), _(u'Planned on')])
        # see all upcoming versions
        if len(rset) == 5:
            rql =  ('Any X,D ORDERBY D DESC WHERE X is Version, X prevision_date D, '
                    'NOT X prevision_date NULL, X in_state S, S name "dev"')
            self.w(u'<a onmouseover=\"$(this).addClass(\'highlighted\')\" ' \
                    'onmouseout=\"$(this).removeClass(\'highlighted\')\" ' \
                    'class="seemore" href="%s">%s</a>' %
                   (xml_escape(self._cw.build_url('view', rql=rql, vid='ooctable')),
                    self._cw._(u'All upcoming versions...')))
        # latest releases
        rset = self._cw.execute(self.latest_releases)
        self.wview('ooctable', rset, 'null',
                   headers=[_(u'Latest releases'), _(u'Published on')])
        # see all latest releases
        if len(rset) == 5:
            rql = ('Any X,D ORDERBY D DESC WHERE X is Version, X publication_date D, '
                   'NOT X publication_date NULL, X in_state S, S name "published"')
            self.w(u'<a onmouseover=\"$(this).addClass(\'highlighted\')\" ' \
                    'onmouseout=\"$(this).removeClass(\'highlighted\')\" ' \
                    'class="seemore" href="%s">%s</a>' %
                   (xml_escape(self._cw.build_url('view', rql=rql, vid='ooctable')),
                    self._cw._(u'All latest releases...')))
        # new projects
        rset = self._cw.execute(self.new_projects)
        self.wview('table', rset, 'null',
                   headers=[_(u'New projects'), _(u'Description')])
        # see all new projects
        if len(rset) == 5:
            rql = 'Any P,S ORDERBY CD DESC WHERE P is Project, P summary S, P creation_date CD'
            self.w(u'<a onmouseover=\"$(this).addClass(\'highlighted\')\" ' \
                    'onmouseout=\"$(this).removeClass(\'highlighted\')\" ' \
                    'class="seemore" href="%s">%s</a>' %
                   (xml_escape(self._cw.build_url('view', rql=rql, vid='table')),
                    self._cw._(u'All new projects...')))
        w(u'</td>')

    def call(self):
        w = self.w
        self._header()
        w(u'<table width="100%"><tr>\n')
        w(u'<td style="width: 50%;">')
        self._left_section()
        self._right_section()
        w(u'</tr></table>\n')


class OOCRsetTableView(tableview.RsetTableView):
    __regid__ = 'ooctable'
    nonfinalvid = 'outofcontext'

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (IndexView,))
    vreg.register_and_replace(IndexView, startup.IndexView)

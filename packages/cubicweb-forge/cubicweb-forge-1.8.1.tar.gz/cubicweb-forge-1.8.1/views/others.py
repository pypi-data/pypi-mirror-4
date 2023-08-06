"""views for other forge entity types: License, TestInstance

:organization: Logilab
:copyright: 2006-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb.predicates import is_instance
from cubicweb.web.views import primary

from cubicweb.selectors import is_instance
from cubicweb.web.views import ibreadcrumbs


class LicensePrimaryView(primary.PrimaryView):
    __select__ = is_instance('License')

    def render_entity_title(self, entity):
        if entity.url:
            title = u'<a href="%s">%s</a>' % (xml_escape(entity.url),
                                              xml_escape(entity.name))
        else:
            title = entity.name
        self.w(u'<h1><span class="etype">%s</span> %s</h1>'
               % (entity.dc_type().capitalize(), title))


class FileIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('File')

    def parent_entity(self):
        return self.entity.project

    def breadcrumbs(self, view=None, recurs=None):
        entity = self.entity
        if entity.reverse_attachment:
            if entity.reverse_attachment[0].e_schema != 'Email':
                ticket = entity.reverse_attachment[0]
                path = ticket.cw_adapt_to('IBreadCrumbs').breadcrumbs(
                    view, recurs or set())
                path.append(entity)
                return path
        if entity.project:
            project = entity.project
            path = project.cw_adapt_to('IBreadCrumbs').breadcrumbs(
                view, recurs or set())
            if entity.reverse_documented_by:
                url = '%s/%s' % (entity.project.absolute_url(), 'documentation')
                label = entity._cw._('documentation')
                path.append( (url, label) )
            path.append(entity)
            return path
        return super(FileIBreadCrumbsAdapter, self).breadcrumbs(view, recurs)


class CardIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('Card')

    def parent_entity(self):
        return self.entity.project

    # XXX should be independant of testcard cube'schema
    def breadcrumbs(self, view=None, recurs=False):
        entity = self.entity
        if entity.project:
            path = entity.project.cw_adapt_to('IBreadCrumbs').breadcrumbs(
                view, recurs or set())
            if entity.reverse_documented_by:
                url = '%s/%s' % (entity.project.absolute_url(), 'documentation')
                path.append( (url, self._cw._('documentation')) )
            elif getattr(entity, 'test_case_for', None):
                path = entity.test_case_for[0].cw_adapt_to('IBreadCrumbs').breadcrumbs(
                    view, recurs or set())
            else:
                url = '%s/%s' % (entity.project.absolute_url(), 'testcases')
                path.append( (url, self._cw._('test cases')) )
            path.append(entity)
            return path
        return super(CardIBreadCrumbsAdapter, self).breadcrumbs(view, recurs)

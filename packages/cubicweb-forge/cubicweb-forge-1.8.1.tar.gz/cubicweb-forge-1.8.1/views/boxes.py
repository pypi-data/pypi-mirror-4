"""forge components boxes

:organization: Logilab
:copyright: 2006-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.mtconverter import xml_escape

from cubicweb.predicates import is_instance, score_entity, has_related_entities
from cubicweb.view import EntityAdapter
from cubicweb.web import component
from cubicweb.web.views import boxes
from cubicweb.utils import transitive_closure_of

class VersionIDownloadableAdapter(EntityAdapter):
    __regid__ = 'IDownloadable'
    __select__ = (is_instance('Version') &
                  score_entity(lambda x: x.project.downloadurl and x.cw_adapt_to('IWorkflowable').state == 'published'))

    def download_url(self):
        downloadurl = self.entity.project.downloadurl
        if not downloadurl:
            return
        if not downloadurl[-1] == '/':
            downloadurl +=  '/'
        return '%s%s' % (downloadurl, self.entity.tarball_name())

    def download_file_name(self):
        return self.entity.tarball_name()

    def download_content_type(self):
        return 'application/x-tar'

    def download_encoding(self):
        return 'gzip'


class ProjectDownloadBox(component.EntityCtxComponent):
    __regid__ = 'download_box'
    __select__ = (component.EntityCtxComponent.__select__
                  & is_instance('Project') &
                  score_entity(lambda x: x.downloadurl and x.latest_version()))
    title = 'download' # no _() to use cw's translation

    def render_body(self, w):
        project = self.entity
        version = project.latest_version()
        w(u'<a href="%s"><img src="%s" alt="%s"/> %s</a>'
          % (xml_escape(version.cw_adapt_to('IDownloadable').download_url()),
             self._cw.uiprops['DOWNLOAD_ICON'],
             self._cw._('download latest version'),
             xml_escape(version.tarball_name())))
        w(u' [<a href="%s">%s</a>]' % (
            project.downloadurl, self._cw._('see them all')))


class FollowupSideboxView(component.EntityCtxComponent):
    __regid__ = 'forge.followup_history'
    __select__ = (component.EntityCtxComponent.__select__ &
                  is_instance('Ticket') &
                  has_related_entities('follow_up', 'object') |
                  has_related_entities('follow_up', 'subject'))

    title = 'ticket traceability chain'
    context = 'incontext'
    wrapper = '<dt class="%s">%s - %s</dt>'

    def render_body(self, w):
        self._cw.add_css('cubes.forge.css')
        ticket = self.entity
        parent = transitive_closure_of(ticket, 'follow_up')
        children = transitive_closure_of(ticket, 'reverse_follow_up')
        w(u'<dl id="tabs">')
        for elt in reversed(list(parent)[1:]):
            w(self.wrapper % ('other',
                              elt.view('incontext'),
                              elt.cw_adapt_to('IWorkflowable').state))
        w(self.wrapper % ('current', ticket.view('incontext'),
                          ticket.cw_adapt_to('IWorkflowable').state))
        for elt in list(children)[1:]:
            w(self.wrapper % ('other',
                              elt.view('incontext'),
                              elt.cw_adapt_to('IWorkflowable').state))
        w(u'</dl>')

class ImageSideboxView(boxes.RsetBox): # XXX Project.screenshots / Ticket.attachment
    __select__ = boxes.RsetBox.__select__ & is_instance('File')

    def render_body(self, w):
        self._cw.add_css('cubes.file.css')
        sample = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        idownloadable = sample.cw_adapt_to('IDownloadable')
        if idownloadable.download_content_type().startswith('image/'):
            icon = idownloadable.download_url(small='true')
        else:
            icon =  self._cw.uiprops['FILE_ICON']
        if getattr(sample, 'reverse_screenshot', None):
            gallery_url = '%s/?tab=screenshots_tab&selected=%s' % (
                sample.project.absolute_url(), sample.eid)
        elif getattr(sample, 'reverse_attachment', None):
            gallery_url = sample.reverse_attachment[0].absolute_url(
                vid='ticketscreenshots', selected=sample.eid)
        elif getattr(sample, 'project', None): # documentation file
            # XXX huumm
            gallery_url = '%s/documentation' % sample.project.absolute_url()
        else:
            gallery_url = u'%s%s' % (self._cw.build_url(vid='gallery',
                                                        rql=self.cw_rset.printable_rql()),
                                     '&selected=%s' % sample.eid)
        if len(self.cw_rset) > 1:
            see_all_url = u'[<a href="%s">%s (%s)</a>]' % (xml_escape(gallery_url),
                                                           self._cw._('see them all'),
                                                           len(self.cw_rset))
        else:
            see_all_url = u''
        w(u'<a href="%s" title="%s"><img alt="" src="%s"/><br/>%s</a><br/>%s'
          % (xml_escape(gallery_url), xml_escape(sample.data_name),
             xml_escape(icon), xml_escape(sample.data_name), see_all_url))


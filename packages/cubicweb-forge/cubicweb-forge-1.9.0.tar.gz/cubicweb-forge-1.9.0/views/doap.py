"""xml/rdf views for forge related entities (doap, linked data)

:organization: Logilab
:copyright: 2001-2010 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.mtconverter import xml_escape

from cubicweb.predicates import is_instance

from cubes.tracker.views import doap as doap_tracker

class ForgeLinkedDataProjectItemView(doap_tracker.LinkedDataProjectItemView):
    __regid__ = 'linked_data_item'
    __select__ = is_instance('Project')

    def cell_call(self, row, col):
        '''display all project attribut and project dependencies and external project (in doap format) if
        it is related to'''
        entity = self.cw_rset.complete_entity(row, col)
        self.w(u' <doap:Project rdf:about="%s">\n' % xml_escape(entity.absolute_url()))
        self.common_doap(entity)
        self.w(u'  <doap:homepage>%s</doap:homepage>\n' % xml_escape(entity.homepage or entity.absolute_url()))
        if entity.downloadurl:
            self.w(u'  <doap:download-page>%s</doap:download-page>\n' % xml_escape(entity.downloadurl))
        self.project_references(entity, 'uses')
        self.project_references(entity, 'recommends')
        self.w(u' </doap:Project>\n')

    def project_references(self, entity, refattr):
        refs = getattr(entity, refattr)
        if refs:
            self.w(u'<%s>' % refattr)
            for ref in refs:
                if ref.e_schema == 'ExtProject':
                    self.w(u'<doap:Project rdf:resource="%s"/>'% xml_escape(ref.homepage))
                else:
                    self.w(u'<doap:Project rdf:resource="%s"/>'% xml_escape(ref.absolute_url()))
            self.w(u'</%s>' % refattr)

class ForgeProjectDoapItemView(ForgeLinkedDataProjectItemView, doap_tracker.ProjectDoapItemView):
    __regid__ = 'doapitem'
    __select__ = is_instance('Project')

    def cell_call(self, row, col):
        """ element as an item for an doap description """
        entity = self.cw_rset.complete_entity(row, col)
        self.w(u'<doap:Project rdf:about="%s">\n' % xml_escape(entity.absolute_url()))
        self.common_doap(entity)
        self.w(u'  <doap:homepage>%s</doap:homepage>\n' % xml_escape(entity.homepage or entity.absolute_url()))
        # version
        ver = entity.latest_version()
        if ver:
            self.w(u'  <doap:release>\n')
            ver.view('doapitem', w=self.w)
            self.w(u'  </doap:release>\n')
        # mailing list
        for ml in entity.reverse_mailinglist_of:
            ml.view('doapitem', w=self.w)
        for lic in entity.reverse_license_of:
            self.w(u'  <doap:license rdf:resource="%s" />\n' % xml_escape(lic.absolute_url()))
        self.w(u'</doap:Project>\n')


class ForgeVersionDoapItemView(doap_tracker.VersionDoapItemView):
    __regid__ = 'doapitem'
    __select__ = is_instance('Version')

    def cell_call(self, row, col):
        """ element as an item for an doap description """
        entity = self.cw_rset.complete_entity(row, col)
        self.w(u'<doap:Version>\n')
        self.w(u'  <doap:revision>%s</doap:revision>\n' % xml_escape(entity.num) )
        self.w(u'  <doap:created>%s</doap:created>\n' % entity.dc_date('%Y-%m-%d'))
        idownloadable = entity.cw_adapt_to('IDownloadable')
        if idownloadable:
            self.w(u'  <doap:download-page>%s</doap:download-page>\n'
                   % xml_escape(idownloadable.download_url()) )
        self.w(u'</doap:Version>\n')

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__,
                      (ForgeLinkedDataProjectItemView,
                       ForgeVersionDoapItemView,
                       ForgeProjectDoapItemView,))
    vreg.register_and_replace(ForgeLinkedDataProjectItemView,
                              doap_tracker.LinkedDataProjectItemView)
    vreg.register_and_replace(ForgeVersionDoapItemView,
                              doap_tracker.VersionDoapItemView)
    vreg.register_and_replace(ForgeProjectDoapItemView,
                              doap_tracker.ProjectDoapItemView)


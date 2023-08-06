"""forge web user interface

:organization: Logilab
:copyright: 2006-2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.predicates import is_instance
from cubicweb.web import uicfg, facet
from cubicweb.web.views.urlrewrite import SchemaBasedRewriter, rgx, build_rset


class ForgeURLRewriter(SchemaBasedRewriter):
    """handle path with the form::

        project/<name>/documentation     -> view project's documentation
        project/<name>/screenshots       -> view project's screenshots
    """
    priority = 10
    rules = [
        (rgx('/project/([^/]+)/documentation'),
         build_rset(rql='Project P WHERE P name %(project)s',
                    rgxgroups=[('project', 1)], vid='projectdocumentation')),
        (rgx('/project/([^/]+)/screenshots'),
         build_rset(rql='Project P WHERE P name %(project)s',
                    rgxgroups=[('project', 1)], vid='projectscreenshots')),
         ]

# XXX some of those tags should be in tracker cube
_afs = uicfg.autoform_section
_afs.tag_attribute(('Version', 'progress_target'), 'main', 'hidden')
_afs.tag_attribute(('Version', 'progress_todo'), 'main', 'hidden')
_afs.tag_attribute(('Version', 'progress_done'), 'main', 'hidden')
_afs.tag_attribute(('Ticket', 'load'), 'main', 'attributes')
_afs.tag_attribute(('Ticket', 'load_left'), 'main', 'attributes')
_afs.tag_attribute(('Ticket', 'load'), 'muledit', 'attributes')
_afs.tag_attribute(('Ticket', 'load_left'), 'muledit', 'attributes')

_pvs = uicfg.primaryview_section

_pvs.tag_object_of(('*', 'documented_by', '*'), 'hidden')

_pvs.tag_subject_of(('Ticket', 'attachment', '*'), 'sideboxes')
_pvs.tag_object_of(('*', 'generate_bug', 'Ticket'), 'sideboxes')

_pvs.tag_subject_of(('Ticket', 'follow_up', '*'), 'hidden')
_pvs.tag_object_of(('*', 'follow_up', 'Ticket'), 'hidden')

_pvs.tag_attribute(('ExtProject', 'name'), 'hidden')

_pvs.tag_attribute(('License', 'name'), 'hidden')
_pvs.tag_attribute(('License', 'url'), 'hidden')

_abaa = uicfg.actionbox_appearsin_addmenu
_abaa.tag_object_of(('*', 'for_version', '*'), False)

_abaa.tag_subject_of(('Ticket', 'attachment', 'File'), True)

_abaa.tag_object_of(('Ticket', 'filed_under', 'Folder'), False)
_abaa.tag_object_of(('Version', 'filed_under', 'Folder'), False)

class TicketHasAttachmentFacet(facet.HasRelationFacet):
    __regid__ = 'forge.attachment-facet'
    __select__ = facet.HasRelationFacet.__select__ & is_instance('Ticket')
    rtype = 'attachment'
    role = 'subject'

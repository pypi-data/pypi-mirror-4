"""some additional tabs for Ticket entities

:organization: Logilab
:copyright: 2006-2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.predicates import one_line_rset, is_instance
from cubicweb.web import component
from cubicweb.web.views import tabs

class TicketTestCardCtxComponent(component.RelatedObjectsCtxComponent):
    """display project's test cards"""
    __regid__ = 'tickettests'
    __select__ = component.RelatedObjectsCtxComponent.__select__ & is_instance('Ticket')

    rtype = 'test_case_for'
    target = 'subject'

    title = _('Test cards')
    context = 'navcontentbottom'
    order = 30

class TicketScreenshotsView(tabs.EntityRelationView):
    """display ticket's screenshots """
    __regid__ = 'ticketscreenshots'
    __select__ = one_line_rset() & tabs.EntityRelationView.__select__ & is_instance('Ticket')

    rtype = 'attachment'
    target = 'object'

    title = _('Attached Documents')
    vid = 'gallery'

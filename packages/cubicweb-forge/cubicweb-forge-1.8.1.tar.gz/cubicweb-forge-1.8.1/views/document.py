"""Restructured text view to export content of a forge instance

:organization: Logilab
:copyright: 2007-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubes.tracker.views import document as document

document.ProjectDocumentItemView.fields += ('homepage',)


class VersionDocumentItemView(document.VersionDocumentItemView):

    def render_attributes(self, entity):
        super(VersionDocumentItemView, self).render_attributes(entity)
        etadate = entity.cw_adapt_to('IMileStone').eta_date()
        if etadate is None:
            etadate = self._cw._('n/a')
        else:
            etadate = self._cw.format_date(etadate)
        self.field(entity, self._cw._('expected date'), etadate)


class TicketDocumentItemView(document.TicketDocumentItemView):
    fields = document.TicketDocumentItemView.fields[:]
    fields.insert(fields.index('state'), 'load')

    def render_child(self, entity):
        if entity.reverse_comments:
            self.w(u'%s ::\n\n' % self._cw.__('Comment_plural'))
            for comment in entity.reverse_comments:
                for line in comment.view('fullthreadtext_descending').splitlines():
                    self.w(u'  ' + line + '\n')
            self.w(u'\n')


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__,
                      (VersionDocumentItemView, TicketDocumentItemView,))
    vreg.register_and_replace(VersionDocumentItemView,
                              document.VersionDocumentItemView)
    vreg.register_and_replace(TicketDocumentItemView,
                              document.TicketDocumentItemView)


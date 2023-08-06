"""some hooks and views to handle notification on forge entity's changes

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb import NoSelectableObject
from cubicweb.predicates import is_instance
from cubicweb.sobjects.notification import StatusChangeMixIn

from cubes.tracker import sobjects as tracker
from cubes.comment import hooks as comment
from cubes.nosylist import sobjects as nosylist


tracker.ProjectAddedView.section_attrs.append('homepage')
tracker.TicketSubmittedView.field_attrs.append('load')


class ProjectStatusChangeView(StatusChangeMixIn, tracker.TrackerEmailView):
    __select__ = is_instance('Project')

    def _subject(self, entity):
        return self._cw._(u'project is now in state "%s"') % (
            self._cw.__(self._kwargs['current_state']))


class CommentAddedView(comment.CommentAddedView):

    def subject(self):
        entity = self.cw_rset.get_entity(0, 0)
        basesubject = super(CommentAddedView, self).subject()
        if entity.project: # may be None if commenting a file used as email attachment
            return u'[%s] %s' % (entity.project.name, basesubject)
        return basesubject


class ProjectRecipientsFinder(nosylist.NosyListRecipientsFinder):
    __select__ = nosylist.NosyListRecipientsFinder.__select__ & \
                 is_instance('Project')

    def recipients(self):
        entity = self.cw_rset.get_entity(0, 0)
        neweids = self._cw.transaction_data.get('neweids', ())
        recipients = super(ProjectRecipientsFinder, self).recipients()
        if entity.eid in neweids:
            try:
                defaultrf = self._cw.vreg['components'].select(self.__regid__, self._cw)
            except NoSelectableObject:
                pass
            else:
                recipients += defaultrf.recipients()
        return recipients


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (CommentAddedView,))
    vreg.register_and_replace(CommentAddedView, comment.CommentAddedView)

"""Forge cube hooks

:organization: Logilab
:copyright: 2006-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from datetime import datetime
from PIL.Image import open as pilopen, ANTIALIAS

from cubicweb import Binary
from cubicweb.server.hook import Hook
from cubicweb.predicates import is_instance
from cubicweb.server import hook

from cubes.tracker import hooks as tracker
from cubes.nosylist import hooks as nosylist


# configure dependency cubes hooks #############################################

tracker.VersionStatusChangeHook.ticket_states_start_version.add('done')
tracker.VersionStatusChangeHook.ticket_states_start_version.add('validation pending')

# permission propagation configuration
# not necessary on: generate_bug, instance_of, recommends, mailinglist_of
tracker.S_RELS |= set(('documented_by', 'attachment', 'screenshot'))
tracker.O_RELS |= set(('test_case_of', 'test_case_for', 'for_version',
                       'comments'))


nosylist.S_RELS |= tracker.S_RELS
nosylist.O_RELS |= tracker.O_RELS


# forge specific hooks #########################################################

class ChangeTicketStateOnVersionStatusChange(Hook):
    __regid__ = 'change_ticket_state_on_version_status_change'
    events = ('after_add_entity',)
    __select__ = Hook.__select__ & is_instance('TrInfo')

    def __call__(self):
        forentity = self.entity.for_entity
        if forentity.e_schema != 'Version':
            return
        if self.entity.new_state.name == 'published':
            for ticket in forentity.reverse_done_in:
                iwf = ticket.cw_adapt_to('IWorkflowable')
                if iwf.state == 'done':
                    msg = self._cw._('version %s published') % forentity.num
                    iwf.fire_transition_if_possible('ask validation',
                                                    comment=msg,
                                                    commentformat=u'text/plain')


class ResetLoadLeftOnTicketStatusChange(Hook):
    __regid__ = 'reset_load_left_on_ticket'
    events = ('after_add_entity',)
    __select__ = Hook.__select__ & is_instance('TrInfo',)

    def __call__(self):
        forentity = self.entity.for_entity
        if forentity.e_schema != 'Ticket':
            return
        newstate = self.entity.new_state.name
        if newstate in ('done', 'rejected', 'deprecated'):
            # ticket is done, set load_left to 0
            attrs = {'load_left': 0}
            if newstate in ('rejected', 'deprecated'):
                # also reset load in that case, we don't want initial estimation
                # to be taken into account
                attrs['load'] = 0
            forentity.set_attributes(**attrs)


class SetTicketLoadLeft(Hook):
    """automatically set load_left according to load if unspecified"""
    __regid__ = 'set_ticket_load'
    events = ('before_add_entity', 'before_update_entity')
    __select__ = Hook.__select__ & is_instance('Ticket',)

    def __call__(self):
        edited = self.entity.cw_edited
        if 'load' in edited and self.entity.load_left is None:
            edited['load_left'] = edited['load']


class SetNosyListBeforeAddComment(Hook):
    """automatically add user who adds a comment to the nosy list"""
    __regid__ = 'set_nosy_list_before_add_comment'
    events = ('after_add_relation',)
    __select__ = Hook.__select__ & hook.match_rtype('comments',)

    def __call__(self):
        if self._cw.is_internal_session:
            return
        comment = self._cw.entity_from_eid(self.eidfrom)
        entity = comment.cw_adapt_to('ITree').root()
        if 'nosy_list' in entity.e_schema.subject_relations():
            x = entity.eid
        else:
            x = comment.eid
        self._cw.execute('SET X nosy_list U WHERE X eid %(x)s, U eid %(u)s, '
                         'NOT X nosy_list U',
                         {'x': x, 'u': self._cw.user.eid})


class SetModificationDateAfterAddComment(Hook):
    """update root entity's modification date after adding a comment"""
    __regid__ = 'set_modification_date_after_comment'
    events = ('after_add_relation',)
    __select__ = Hook.__select__ & hook.match_rtype('comments',)

    def __call__(self):
        entity = self._cw.entity_from_eid(self.eidto)
        while entity.e_schema == 'Comment':
            entity = entity.cw_adapt_to('ITree').root()
        entity.set_attributes(modification_date=datetime.now())


class TicketDoneInProgressHook(Hook):
    __regid__ = 'ticket_done_in_progress'
    __select__ = Hook.__select__ & hook.match_rtype('done_in',)
    events = ('after_add_relation', 'after_delete_relation', )

    def __call__(self):
        version = self._cw.entity_from_eid(self.eidto)
        version.update_progress()


class TicketProgressHook(Hook):
    __regid__ = 'ticket_progress'
    __select__ = Hook.__select__ & is_instance('Ticket',)
    events = ('after_update_entity', )

    def __call__(self):
        if 'load' in self.entity.cw_edited or \
               'load_left' in self.entity.cw_edited:
            try:
                self.entity.done_in[0].update_progress()
            except IndexError:
                # not yet attached to a version
                pass

class SetProjectIcon(hook.Hook):
    """Set meta-attributes icon_format, icon_name and resize the image file"""
    __regid__ = 'forge.set_project_icon_metadata'
    __select__ = is_instance('Project')
    events = ('before_add_entity', 'before_update_entity')

    def __call__(self):
        project = self.entity
        icon = project.cw_edited.get('icon')
        if icon is not None:
            try:
                img = pilopen(Binary(icon.getvalue()))
            except IOError:
                # XXX Here we should:
                #raise ValueError('The icon file does not appear to be a valid image.')
                # and add `icon` and `icon_format` to `ignored_relations` in
                # test_forge to skip automatic population. Unfortunately, the
                # latter does not work, so we simply:
                return
            fmt = img.format
            project.cw_edited['icon_format'] = unicode('image/%s' % fmt.lower())
            img.thumbnail((50, 50), ANTIALIAS)
            stream = Binary()
            img.save(stream, fmt)
            stream.seek(0)
            project.cw_edited['icon'] = stream

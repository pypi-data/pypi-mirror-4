from copy import copy

from cubicweb.web import stdmsgs, formwidgets, eid_param
from cubicweb.web.formfields import RelationField
from cubicweb.web.views.workflow import ChangeStateFormView
from cubicweb.predicates import is_instance, is_in_state, match_transition

class NotValidatedChangeView(ChangeStateFormView):

    __select__ = (ChangeStateFormView.__select__ &
                  is_instance('Ticket') &
                  is_in_state('validation pending') &
                  match_transition('refuse validation'))

    def cell_call(self, row, col):
        ""
        entity = self.cw_rset.get_entity(row, col)
        transition = self._cw.entity_from_eid(self._cw.form['treid'])
        form = self.get_form(entity, transition)
        self.w(u'<h4>%s %s</h4>\n' % (self._cw._(transition.name),
                                      entity.view('oneline')))
        msg = self._cw.__('status will change from %(st1)s to %(st2)s') % {
            'st1': entity.cw_adapt_to('IWorkflowable').printable_state,
            'st2': self._cw._(transition.destination(entity).name)}
        self.w(u'<p>%s</p>\n' % msg)
        self.w('<h4>%s</h4>\n' % self._cw._('A new ticket following-up the former must be created'))
        form.render(w=self.w)

    def get_form(self, entity, transition, **kwargs):
        """Select the ticket creation form and mixed it with the
        workflow comment form
        """
        buttons = [formwidgets.SubmitButton(),
                   formwidgets.Button(stdmsgs.BUTTON_CANCEL, cwaction='cancel')]
        entity.complete()
        entity.cw_attr_cache.pop('load_left', None)
        followup_tk = copy(entity)
        followup_tk.eid = self._cw.varmaker.next()
        form = self._cw.vreg['forms'].select('composite', self._cw,
                                             domid='followupdform',
                                             form_buttons=buttons,
                                             form_renderer_id = 'base',
                                             redirect_path=self.redirectpath(entity),
                                             **kwargs)

        followup_form = self._cw.vreg['forms'].select('edition', self._cw,
                                                       entity=followup_tk,
                                                       mainform=False)
        followup_form.add_hidden(eid_param('__cloned_eid', followup_tk.eid),
                                 entity.eid)
        followup_field = RelationField(
            name='follow_up', role='subject', eidparam=True,
            choices=[(entity.dc_title(), unicode(entity.eid))])
        followup_form.append_field(followup_field)
        form.add_subform(followup_form)
        trinfo = self._cw.vreg['etypes'].etype_class('TrInfo')(self._cw)
        trinfo.eid = self._cw.varmaker.next()
        wf_form =  self._cw.vreg['forms'].select('edition',
                                                 self._cw,
                                                 entity=trinfo,
                                                 mainform=False)
        wf_form.field_by_name('wf_info_for', 'subject').value = entity.eid
        trfield = wf_form.field_by_name('by_transition', 'subject')
        trfield.widget = formwidgets.HiddenInput()
        trfield.value = transition.eid
        form.add_subform(wf_form)
        return form

def registration_callback(vreg):
    vreg.register(NotValidatedChangeView)

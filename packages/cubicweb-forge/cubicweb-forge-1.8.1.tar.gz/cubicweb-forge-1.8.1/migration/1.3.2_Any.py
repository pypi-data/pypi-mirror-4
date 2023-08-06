session.set_pool()

wf = rql('Workflow X WHERE ET default_workflow X, ET name "Ticket"') .get_entity(0, 0) # suppose it's forge workflow...

# remove confirm/confirmed transition and state
# <XXX wf.replace_state('confirmed', 'done')>
session.execute('SET X in_state S WHERE X is Ticket, X in_state CS, CS name "confirmed", S name "open", S state_of WF, ET default_workflow WF, ET name "Ticket"')
session.execute('SET X from_state S WHERE T is Ticket, X wf_info_for T, X from_state CS, CS name "confirmed", S name "open", S state_of WF, ET default_workflow WF, ET name "Ticket"')
session.execute('SET X to_state S WHERE T is Ticket, X wf_info_for T, X to_state CS, CS name "confirmed", S name "open", S state_of WF, ET default_workflow WF, ET name "Ticket"')
checkpoint()
confirmed = wf.state_by_name('confirmed')
confirmed and confirmed.delete()
# </XXX>

confirm = wf.transition_by_name('confirm')
confirm and confirm.delete()
# insert 'done' state:  ---[done]--> done ---[ask validation]--> validation pending
done = wf.add_state('done')
wf.transition_by_name('done').set_relations(destination_state=done)
wf.transition_by_name('stop').set_relations(destination_state=wf.state_by_name('open'))
wf.add_transition('ask validation', done, wf.state_by_name('validation pending'),
                  conditions='X done_in V, V in_state S, S name "published"')
checkpoint()


sync_schema_props_perms(('Version', 'depends_on', 'Version'))
sync_schema_props_perms(('Version', 'conflicts', 'Version'))
checkpoint()

drop_attribute('Project', 'vcsurl')
drop_attribute('Project', 'reporturl')


add_relation_definition('Ticket', 'follow_up', 'Ticket')

# Update the Ticket workflow

from cubes.tracker.schemaperms import xperm

wf = get_workflow_for('Ticket')
vp = wf.state_by_name('validation pending')
notvalidated = wf.add_state('not validated')
wf.add_transition(_('refuse validation'), (vp,), notvalidated,
                  ('managers', 'staff'), xperm('client'))
reopen = wf.transition_by_name('reopen')
rql('DELETE S allowed_transition TR WHERE S eid %(s)s, TR eid %(tr)s',
    {'s': vp.eid, 'tr': reopen.eid})
commit()

sync_schema_props_perms('done_in')

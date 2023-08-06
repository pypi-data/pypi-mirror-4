from cubes.tracker.schemaperms import xperm

# allow transition from done to reopen
rql('SET S allowed_transition T '
    'WHERE S state_of W, S name "done", '
    'T transition_of W, T name "reopen", '
    'W workflow_of ET, ET name "Ticket"')
# allow transition from in-progress to waiting for feedback
rql('SET S allowed_transition T '
    'WHERE S state_of W, S name "in-progress", '
    'T transition_of W, T name "wait for feedback", '
    'W workflow_of ET, ET name "Ticket"')
# turn the got feedback transition to a 'go back' transition
rql('DELETE T destination_state S '
    'WHERE T transition_of W, T name "got feedback", '
    'W workflow_of ET, ET name "Ticket"')
# grant permission to client to pass the 'got feedback' transition
tr = rql('Transition T WHERE T transition_of W, T name "got feedback", '
         'W workflow_of ET, ET name "Ticket"').get_entity(0, 0)
tr.set_permissions(('managers', 'staff'), xperm('client', 'developer'))

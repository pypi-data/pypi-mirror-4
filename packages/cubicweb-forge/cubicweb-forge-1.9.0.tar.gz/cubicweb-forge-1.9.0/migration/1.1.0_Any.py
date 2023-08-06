from os.path import join
from cubicweb.server.sqlutils import sqlexec

add_cube('tracker', update_database=False)

# Add nosy_list for Project and Ticket, add interested_in for Ticket

add_relation_type('nosy_list')
add_relation_definition('CWUser', 'interested_in', 'Ticket')
#rql('SET U interested_in T WHERE U interested_in P, P is Project, U is CWUser, T concerns P, T is Ticket')
rql('SET P nosy_list U WHERE U interested_in P, P is Project, U is CWUser')
checkpoint()

if repo.system_source.dbdriver == 'postgres':
    from cubes import tracker
    pgproc = join(tracker.__path__[0], 'schema', '_regproc.sql.postgres')
    sqlexec(open(pgproc).read(), sql, False, delimiter=';;')
    checkpoint()

sync_schema_props_perms(('Project','name', 'String'), syncperms=False)

# add computed attributes to Version
for attr in ('progress_target', 'progress_done', 'progress_todo'):
    add_attribute('Version', attr)

for entity in rql('Any X WHERE X is Version', ask_confirm=False).entities():
    entity.update_progress()
checkpoint()


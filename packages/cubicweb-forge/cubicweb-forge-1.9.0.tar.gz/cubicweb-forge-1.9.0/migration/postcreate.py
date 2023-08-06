"""forge post creation script, set application's workflows

:organization: Logilab
:copyright: 2003-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubes.localperms import xperm

# Project workflow
pwf = add_workflow(_('default project workflow'), 'Project')

active = pwf.add_state(_('active development'), initial=True)
asleep = pwf.add_state(_('asleep'))
dead   = pwf.add_state(_('no more maintained'))
moved  = pwf.add_state(_('moved'))

pwf.add_transition(_('temporarily stop development'), active, asleep,
                   ('managers', 'staff'), 'U has_update_permission X')
pwf.add_transition(_('stop maintainance'), (active, asleep), dead,
                   ('managers', 'staff'), 'U has_update_permission X')
pwf.add_transition(_('restart development'), (asleep, dead), active,
                   ('managers', 'staff'), 'U has_update_permission X')
pwf.add_transition(_('project moved'), (active, asleep), moved,
                   ('managers', 'staff'), 'U has_update_permission X')


# Ticket workflow
twf = add_workflow(_('forge ticket workflow'), 'Ticket')

open       = twf.add_state(_('open'), initial=True)
waiting    = twf.add_state(_('waiting feedback'))
rejected   = twf.add_state(_('rejected'))
inprogress = twf.add_state(_('in-progress'))
done       = twf.add_state(_('done'))
vp         = twf.add_state(_('validation pending'))
resolved   = twf.add_state(_('resolved'))
deprecated = twf.add_state(_('deprecated'))
notvalidated = twf.add_state(_('not validated'))

twf.add_transition(_('start'), open, inprogress,
                   ('managers', 'staff'), xperm('developer'))
twf.add_transition(_('reject'), (open, inprogress), rejected,
                   ('managers', 'staff'), xperm('developer'))
twf.add_transition(_('done'), (open, inprogress), done,
                   ('managers', 'staff'), xperm('developer'))
twf.add_transition(_('ask validation'), done, vp,
                   ('managers', 'staff'), xperm('developer'))
twf.add_transition(_('deprecate'), open, deprecated,
                   ('managers', 'staff'), xperm('client', 'developer'))
twf.add_transition(_('resolve'), vp, resolved,
                   ('managers', 'staff'), xperm('client'))
twf.add_transition(_('reopen'), (done, rejected), open,
                   ('managers', 'staff'), xperm('client'))
twf.add_transition(_('refuse validation'), (vp,), notvalidated,
                   ('managers', 'staff'), xperm('client'))
twf.add_transition(_('wait for feedback'), (open, inprogress), waiting,
                   ('managers', 'staff'), xperm('developer'))
twf.add_transition(_('got feedback'), waiting, None, # go back transition
                   ('managers', 'staff'), xperm('client', 'developer'))

# try to find some licenses with devtools
try:
    from logilab.devtools.lib.pkginfo import get_known_licenses, TEMPLATE_DIR
    import codecs
    import os, os.path as osp
    licenses_dir = osp.join(TEMPLATE_DIR, 'licenses')
    for license_name in get_known_licenses():
        shortdesc_filename = osp.join(licenses_dir, '%s.txt' % license_name)
        longdesc_filename = osp.join(licenses_dir, 'full_%s.txt' % license_name)
        args = {'name' : unicode(license_name)}
        try:
            args['short_desc'] = codecs.open(shortdesc_filename, encoding='iso-8859-1').read()
            args['long_desc'] = codecs.open(longdesc_filename, encoding='iso-8859-1').read()
        except IOError:
            args['short_desc'] = u''
            args['long_desc'] = u''
        rql('INSERT License L: L name %(name)s, L shortdesc %(short_desc)s, L longdesc %(long_desc)s', args)
except ImportError:
    import sys
    print >> sys.stderr, "I was unable to import devtools, You will have to create " \
          "license entities yourself"

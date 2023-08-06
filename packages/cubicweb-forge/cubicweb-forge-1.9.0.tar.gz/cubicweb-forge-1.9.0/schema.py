"""forge application'schema

Security groups :
* managers (eg site admins)
* users (every authenticated users)
* guests (anonymous users)
* staff (subset of users)

Local permission (granted by project):
* developer
  * XXX describe
* client:
  * add version
  * add ticket
  * add/remove tickets from version in the 'planned' state
  * add/delete test cards
  * add documentation file, screenshots, ticket's attachment

:organization: Logilab
:copyright: 2003-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from yams.buildobjs import (EntityType, RelationDefinition,
                            String, Float, RichString, Bytes)

from cubicweb.schema import (RQLVocabularyConstraint, RRQLExpression,
                             ERQLExpression, make_workflowable)
from cubes.localperms import sexpr, xexpr, xrexpr, xperm, restricted_oexpr

from cubes.tracker.schema import Project, Ticket, Version, done_in
from cubes.file.schema import File
from cubes.card.schema import Card

Project.add_relation(Bytes(description=_("project icon")), name='icon')
Project.add_relation(String(meta=True, maxsize=50), name='icon_format')

Project.add_relation(String(maxsize=128,
                            description=_('url to project\'s home page. Leave this field '
                                          'empty if the project is fully hosted here.')),
                     name='homepage')
Project.add_relation(String(maxsize=256,
                            description=_('url to access tarball for releases of the project')),
                     name='downloadurl')

Project.get_relations('uses').next().constraints = [
    RQLVocabularyConstraint('S in_state SST, SST name "active development", '
                            'O in_state OST, OST name "active development", '
                            'NOT O uses S')
    ]

make_workflowable(Project)

done_in.__permissions__['delete'] = (
    'managers',
    RRQLExpression('U in_group G, G name "staff", NOT (O in_state ST, ST name "published")'),
    restricted_oexpr('O in_state ST, ST name "planned"', 'client'),)

class recommends(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', RRQLExpression('U has_update_permission S', 'S'),),
        'delete': ('managers', RRQLExpression('U has_update_permission S', 'S'),),
        }
    subject = object = 'Project'
    constraints = [
        RQLVocabularyConstraint('S in_state SST, SST name "active development", '
                                'O in_state OST, OST name "active development", '
                                'NOT O recommends S')
        ]
    description = _('project\'s optional dependencies')


class documented_by(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', sexpr('developer', 'client'),),
        'delete': ('managers', 'staff', sexpr('developer', 'client'),),
    }
    subject = 'Project'
    object = ('Card', 'File')
    constraints = [RQLVocabularyConstraint('S in_state ST, ST name "active development"')]
    description = _('project\'s documentation')


class screenshot(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', sexpr('developer', 'client'),),
        'delete': ('managers', 'staff', sexpr('developer', 'client'),),
    }
    subject = 'Project'
    object = 'File'
    constraints = [RQLVocabularyConstraint('S in_state ST, ST name "active development"')]
    description = _('project\'s screenshot')


class mailinglist_of(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', RRQLExpression('U has_update_permission O', 'O'),),
        'delete': ('managers', RRQLExpression('U has_update_permission O', 'O'),),
        }
    subject = 'MailingList'
    object = 'Project'
    cardinality = '*?'
    description = _("Project's related mailing list")


class ExtProject(EntityType):
    """project developed externally of the cubicweb forge application"""
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', 'staff',),
        'update': ('managers', 'staff', 'owners',),
        'delete': ('managers', 'owners'),
        }

    name = String(required=True, fulltextindexed=True, unique=True, maxsize=32)
    description = RichString(fulltextindexed=True, maxsize=512)
    homepage  = String(maxsize=128, description=_('url to project\'s home page.'))



Ticket.add_relation(Float(description=_('load for this ticket in day.man')),
                    name='load')
Ticket.add_relation(Float(description=_('remaining load for this ticket in day.man')),
                    name='load_left')

Ticket.get_relations('concerns').next().constraints = [
    RQLVocabularyConstraint('O in_state ST, ST name "active development"')
    ]

# client can only modify tickets when they are in the "open" state
Ticket.__permissions__['update'] = ('managers', 'staff',
                                    xexpr('developer'),
                                    # XXX use cost is NULL instead
                                    ERQLExpression(xperm('client')+', X in_state S, S name "open"'),
                                    ERQLExpression('X owned_by U, X in_state S, S name "open"'),
                                    )

class follow_up(RelationDefinition):
    """link a ticket to another, not validated, ticket"""
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', RRQLExpression(xperm('client'))),
        'delete': ('managers',),
        }
    subject = 'Ticket'
    object = 'Ticket'
    cardinality = '??'

class attachment(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        # also used for Email attachment File
        'add':    ('managers', 'staff', RRQLExpression('U has_update_permission S', 'S')),
        'delete': ('managers', 'staff', RRQLExpression('U has_update_permission S', 'S')),
    }
    subject = 'Ticket'
    object = 'File'
    description = _('files related to this ticket (screenshot, file needed to '
                    'reproduce a bug...)')


Version.add_relation(Float(description=_('computed attribute'), default=0), name='progress_target')
Version.add_relation(Float(description=_('computed attribute'), default=0), name='progress_done')
Version.add_relation(Float(description=_('computed attribute'), default=0), name='progress_todo')
Version.get_relations('version_of').next().constraints = [
    RQLVocabularyConstraint('O in_state ST, ST name "active development"')
    ]
Version.get_relations('depends_on').next().constraints[0].expression += ' OR EXISTS(PS recommends PO)'
Version.get_relations('conflicts').next().constraints[0].expression += ' OR EXISTS(PS recommends PO)'

class License(EntityType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', ),
        'update': ('managers', 'owners',),
        'delete': ('managers', 'owners'),
        }
    ## attributes
    name  = String(required=True, fulltextindexed=True, unique=True, maxsize=64)
    # XXX shortesc is actually licence's disclaimer
    shortdesc = String(required=False, fulltextindexed=True, description=_('disclaimer of the license'))
    longdesc = RichString(required=False, fulltextindexed=True, description=_("full license's text"))
    url = String(maxsize=256)


class license_of(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', RRQLExpression('U has_update_permission O', 'O'),),
        'delete': ('managers', RRQLExpression('U has_update_permission O', 'O'),),
        }
    subject = 'License'
    object = 'Project'
    cardinality = '**'
    description = _("Project's license")


File.__permissions__ = {
    'read':   ('managers', 'users', 'guests'),
    'add':    ('managers', 'staff',
               ERQLExpression('Y attachment X, Y is Email, U has_update_permission Y'),
               xrexpr('attachment', 'File', 'developer', 'client', role='object'),
               xrexpr('screenshot', 'File', 'developer', 'client', role='object'),
               xrexpr('documented_by', 'File', 'developer', 'client', role='object'),),
    'update': ('managers', 'staff', 'owners',),
    'delete': ('managers', 'owners'),
    }

# XXX should be independant of testcard cube'schema
Card.__permissions__ = {
    'read':   ('managers', 'users', 'guests'),
    'add':    ('managers', 'staff',
               xrexpr('documented_by', 'Card', 'developer', 'client', role='object'),
               xrexpr('test_case_for', 'developer', 'client'),
               xrexpr('test_case_of', 'developer', 'client'),),
    'update': ('managers', 'staff', 'owners',),
    'delete': ('managers', 'owners'),
    }

# nosy list configuration ######################################################

class interested_in(RelationDefinition):
    '''users to notify of changes concerning this entity'''
    subject = 'CWUser'
    object = ('Project', 'Ticket')

class nosy_list(RelationDefinition):
    subject = ('Email', 'ExtProject', 'Project', 'Version', 'Ticket',
               'Comment', 'File', 'Card', 'TestInstance')
    object = 'CWUser'

# extra relation definitions ##################################################

class see_also(RelationDefinition):
    symmetric = True
    subject = ('ExtProject', 'Project', 'Ticket', 'Card', 'File', 'Email')
    object = ('ExtProject', 'Project', 'Ticket', 'Card', 'File', 'Email')

class comments(RelationDefinition):
    subject = 'Comment'
    object = ('Ticket', 'Card', 'File', 'Email')
    cardinality = '1*'
    composite = 'object'


class tags(RelationDefinition):
    subject = 'Tag'
    object = ('ExtProject', 'Project', 'Version', 'Ticket',
              'License', 'MailingList',
              'Card', 'File', 'Email')

class filed_under(RelationDefinition):
    subject = ('ExtProject', 'Project', 'Card', 'File')
    object = 'Folder'

class require_permission(RelationDefinition):
    subject = ('ExtProject', 'Comment', 'File', 'Card', 'TestInstance')
    object = 'CWPermission'

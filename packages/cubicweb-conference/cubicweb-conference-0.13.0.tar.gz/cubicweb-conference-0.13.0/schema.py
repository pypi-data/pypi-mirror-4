from yams.buildobjs import (
    EntityType, String, Date, SubjectRelation, Datetime, RichString,
    RelationDefinition, Boolean)
from yams.constraints import SizeConstraint, BoundaryConstraint, Attribute


from cubicweb.schema import (
    ERQLExpression, RRQLExpression, WorkflowableEntityType,
    RQLVocabularyConstraint)
from cubicweb.schemas.base import CWUser

CWUser.add_relation(SubjectRelation('Talk', cardinality='**'), name='attend')

CWUser.add_relation(String(), name='representing')
CWUser.__permissions__['read'] = ('managers', 'users', 'guests')

def user_owns_subject():
    return RRQLExpression('S owned_by U')

def user_owns_object():
    return RRQLExpression('O owned_by U')

def user_is_chair():
    return ERQLExpression('U is_chair_at C, X in_conf C')

def user_is_chair_subject():
    return RRQLExpression('U is_chair_at C, S in_conf C')

def user_is_chair_object():
    return RRQLExpression('U is_chair_at C, O in_conf C')

def user_chairs_object():
    return RRQLExpression('U is_chair_at O')

class leads(RelationDefinition):
    subject = 'CWUser'
    object = 'Talk'
    cardinality = '*+'
    constraints = [RQLVocabularyConstraint('S in_group G, G name "users"')]
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', user_is_chair_object(), user_owns_object()),
        'delete': ('managers', user_is_chair_object(), user_owns_object()),
        }

class Conference(WorkflowableEntityType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', ),
        'update': ('managers', 'owners', ERQLExpression('U is_chair_at X'),),
        'delete': ('managers', 'owners',),
        }
    title = String(maxsize=50, required=True, fulltextindexed=True)
    url_id = String(maxsize=50, required=True, unique=True,
                    description=_('unique conference identifier for url'))
    start_on = Date(default='TODAY', required=True, constraints=[BoundaryConstraint('<=', Attribute('end_on'))])
    end_on = Date(default='TODAY', required=True, constraints=[BoundaryConstraint('>=', Attribute('start_on'))])
    description = RichString(fulltextindexed=True)
    call_open = Boolean(default=False)
    reg_open = Boolean(default=False)

class Track(EntityType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', user_is_chair()),
        'update': ('managers', 'owners', user_is_chair()),
        'delete': ('managers', 'owners', user_is_chair()),
        }
    title = String(maxsize=50, required=True, fulltextindexed=True)
    description = RichString(fulltextindexed=True)

class Talk(WorkflowableEntityType):
    __permissions__ = {
        'read':   ('managers', user_is_chair(),
                   ERQLExpression('X owned_by U'),
                   ERQLExpression('X in_state ST, ST name "accepted"'),
                   ERQLExpression('U reviews X, X in_state ST, '
                                  'ST name in ("correction", "inreview", "rejected", '
                                  '"accept_pending", "reject_pending")'),
                   ),
        'add':    ('managers', 'users'),
        'update': ('managers', user_is_chair(),
                   ERQLExpression('X in_state ST, ST name in ("draft", "correction"), X owned_by U')),
        'delete': ('managers', user_is_chair()),
        }
    title = String(maxsize=200, required=True, fulltextindexed=True)
    description = RichString(fulltextindexed=True)
    start_time = Datetime(__permissions__={
        'read':   ('managers', 'users', 'guests',),
        'update': ('managers', user_is_chair()),
        }, constraints=[BoundaryConstraint('<', Attribute('end_time'))])
    end_time = Datetime(__permissions__={
        'read':   ('managers', 'users', 'guests',),
        'update': ('managers', user_is_chair()),
        }, constraints=[BoundaryConstraint('>', Attribute('start_time'))])

class comments(RelationDefinition):
    subject = 'Comment'
    object = 'Talk'
    cardinality='1*'

class location(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'update': ('managers', user_is_chair())
        }
    subject = 'Talk'
    object = 'String'
    cardinality = '?1'
    constraints=[SizeConstraint(100)]

class in_track(RelationDefinition):
     __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', user_is_chair_subject(), user_owns_subject()),
        'delete': ('managers', user_is_chair_subject(), user_owns_subject()),
        }
     subject = 'Talk'
     object = 'Track'
     cardinality = '?*'

class has_attachments(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', user_is_chair_subject(), user_owns_subject()),
        'delete': ('managers', user_is_chair_subject(), user_owns_subject()),
        }
    subject = 'Talk'
    object = 'File'
    cardinality = '*?'

class tags(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', user_is_chair_object()),
        'delete': ('managers', user_is_chair_object()),
        }
    subject = 'Tag'
    object = 'Talk'

class track_in_conf(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', user_chairs_object()),
        'delete': ('managers', user_chairs_object()),
        }
    name = 'in_conf'
    subject = 'Track'
    object = 'Conference'
    cardinality = '1*'

class talk_in_conf(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', 'users'),
        'delete': ('managers', user_chairs_object()),
        }
    name = 'in_conf'
    subject = 'Talk'
    object = 'Conference'
    cardinality = '1*'

class reviews(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users',),
        'add':    ('managers', user_chairs_object()),
        'delete': ('managers', user_chairs_object()),
        }
    subject = ('CWUser',)
    object = 'Talk'
    cardinality = '**'

class Sponsor(EntityType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', user_is_chair()),
        'update': ('managers', 'owners', user_is_chair()),
        'delete': ('managers', 'owners'),
        }
    title = String(maxsize=100, required=True, fulltextindexed=True)
    description = RichString(fulltextindexed=True)
    url = String(maxsize=100)

class has_logo(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', user_owns_subject()),
        'delete': ('managers', user_owns_subject()),
        }
    subject = ('Sponsor',)
    object = 'File'
    cardinality = '1*'
    composite = 'subject'

# Sponsor is_sponsor SponsorShip sponsoring_conf Conference

class SponsorShip(EntityType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', user_is_chair()),
        'update': ('managers', user_is_chair()),
        'delete': ('managers', user_is_chair()),
        }
    title = String(maxsize=100, required=True, fulltextindexed=True)
    level = String(vocabulary=('Gold', 'Silver', 'Bronze', 'Media'))

class sponsoring_conf(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', user_chairs_object()),
        'delete': ('managers', user_chairs_object()),
        }
    subject = ('SponsorShip',)
    object = 'Conference'
    cardinality = '+*'

class is_sponsor(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', ),
        'delete': ('managers', ),
        }
    subject = ('Sponsor',)
    object = ('SponsorShip',)
    cardinality = '**'

# roles

class is_chair_at(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', ),
        'delete': ('managers', ),
        }
    subject = ('CWUser',)
    object = ('Conference',)
    cardinality = '**'

class is_reviewer_at(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', user_chairs_object()),
        'delete': ('managers', user_chairs_object()),
        }
    subject = ('CWUser',)
    object = ('Conference',)
    cardinality = '**'

class take_place_at(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', user_is_chair_subject()),
        'delete': ('managers', user_is_chair_subject())
        }
    name = 'take_place_at'
    subject = 'Conference'
    object = ('PostalAddress',)
    cardinality = '+*'

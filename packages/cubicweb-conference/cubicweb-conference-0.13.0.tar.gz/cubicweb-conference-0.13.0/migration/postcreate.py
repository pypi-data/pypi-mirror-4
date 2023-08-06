# postcreate script. You could setup a workflow here for example

_ = unicode

# constants used for permissions

TALK_CHAIR = 'U is_chair_at C, X in_conf C, X is Talk'
CONF_CHAIR = 'U is_chair_at X'
REVIEWER = 'U is_reviewer_at C, X in_conf C'
OWNER_CALL_OPEN = 'X owned_by U, X in_conf C, C call_open True'
MANAGER = ('managers',)
OWNER_MANAGER = ('owners', 'managers')

# Conference Workflow

def define_conference_workflow():
    twf = add_workflow(_('conference workflow'), 'Conference')
    planned = twf.add_state(_('planned'), initial=True)
    scheduled = twf.add_state(_('scheduled'))
    archived = twf.add_state(_('archived'))
    twf.add_transition(_('schedule'), (planned,), scheduled, MANAGER, conditions=CONF_CHAIR)
    twf.add_transition(_('archive'), (scheduled,), archived, MANAGER, conditions=CONF_CHAIR)

define_conference_workflow()

# Talk Workflow

def define_talk_workflow():
    twf = add_workflow(_('talk workflow'), 'Talk')
    draft = twf.add_state(_('draft'), initial=True)
    submitted = twf.add_state(_('submitted'))
    correction = twf.add_state(_('correction'))
    inreview = twf.add_state(_('inreview'))
    accept_pending = twf.add_state(_('accept_pending'))
    reject_pending = twf.add_state(_('reject_pending'))
    accepted = twf.add_state(_('accepted'))
    rejected = twf.add_state(_('rejected'))
    twf.add_transition(_('submit your work'), (draft,), submitted, MANAGER, conditions=(TALK_CHAIR,OWNER_CALL_OPEN))
    twf.add_transition(_('redraft'), (submitted,), draft, MANAGER, conditions=(TALK_CHAIR,OWNER_CALL_OPEN))
    twf.add_transition(_('send to reviewer'), (submitted,), inreview, MANAGER, conditions=TALK_CHAIR)
    twf.add_transition(_('need correction'), (inreview,), correction, MANAGER, conditions=(REVIEWER,TALK_CHAIR))
    twf.add_transition(_('resend to reviewer'), (correction,), inreview, OWNER_MANAGER, conditions=TALK_CHAIR)
    twf.add_transition(_('propose to accept'), (inreview,), accept_pending, MANAGER, conditions=(REVIEWER,TALK_CHAIR))
    twf.add_transition(_('propose to reject'), (inreview,), reject_pending, MANAGER, conditions=(REVIEWER,TALK_CHAIR))
    twf.add_transition(_('need more review'), (accept_pending,reject_pending), inreview, MANAGER, conditions=(REVIEWER,TALK_CHAIR))
    twf.add_transition(_('accept talk'), (accept_pending,reject_pending), accepted, MANAGER, conditions=TALK_CHAIR)
    twf.add_transition(_('reject talk'), (reject_pending,accept_pending), rejected, MANAGER, conditions=TALK_CHAIR)

define_talk_workflow()

commit()

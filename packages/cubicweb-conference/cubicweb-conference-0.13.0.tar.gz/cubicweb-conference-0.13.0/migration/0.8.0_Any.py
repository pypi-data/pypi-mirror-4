CHAIR = 'U is_chair_at C, X in_conf C'
REVIEWER = 'U is_reviewer_at C, X in_conf C'
MANAGER = ('managers',)

twf = rql('Any W WHERE W is Workflow, W workflow_of X, X name "Talk"', ask_confirm=False).get_entity(0,0)
for state in twf.reverse_state_of:
    if state.name == 'accepted':
        accepted = state
    elif state.name == 'rejected':
        rejected = state
    elif state.name == 'inreview':
        inreview = state

# add new states
accept_pending = twf.add_state(_('accept_pending'))
reject_pending = twf.add_state(_('reject_pending'))

# modify existing transitions
for transition in twf.reverse_transition_of:
    if transition.name == u'accept talk':
        transition.set_attributes(name=u'propose to accept')
        transition.set_relations(destination_state=accept_pending)
    elif transition.name == u'reject talk':
        transition.set_attributes(name=u'propose to reject')
        transition.set_relations(destination_state=reject_pending)

# add new transitions
twf.add_transition(_('accept talk'), (accept_pending,reject_pending), accepted, MANAGER, conditions=CHAIR)
twf.add_transition(_('reject talk'), (accept_pending,reject_pending), rejected, MANAGER, conditions=CHAIR)
twf.add_transition(_('need more review'), (accept_pending,reject_pending), inreview, MANAGER, conditions=(REVIEWER,CHAIR))

commit()

sync_schema_props_perms()

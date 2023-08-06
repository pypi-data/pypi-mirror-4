# add attributes to Conference
add_attribute('Conference', 'call_open')
add_attribute('Conference', 'reg_open')

# add relations
add_relation_type('is_chair_at')
add_relation_type('is_reviewer_at')
add_relation_type('is_delegate_at')

# assuming the db is correct, propagate
rql('SET U is_reviewer_at C WHERE U reviews T, T in_conf C')

commit()

# remove group moderators
rql('SET X in_group U WHERE X in_group G, G name "moderators", U is CWGroup, U name "users"')
rql('DELETE CWGroup G WHERE G name "moderators"')

# get talk workflow
twf = rql('Any W WHERE W is Workflow, W workflow_of X, X name "Talk"', ask_confirm=False).get_entity(0,0)

# fix old migration problem
for transition in twf.reverse_transition_of:
    if transition.name == u'ask for correction':
        transition.set_attributes(name=u'need correction')

# add redraft transition
for state in twf.reverse_state_of:
    if state.name == 'draft':
        draft = state
    elif state.name == 'submitted':
        submitted = state
twf.add_transition(_('redraft'), (submitted,), draft, ('owners','managers',))

# change workflow permissions
CHAIR = 'U is_chair_at C, X in_conf C'
REVIEWER = 'U is_reviewer_at C, X in_conf C'
OWNER_CALL_OPEN = 'X owned_by U, X in_conf C, C call_open "True"'
MANAGER = ('managers',)
OWNER_MANAGER = ('owners', 'managers')

for transition in twf.reverse_transition_of:
    if transition.name == 'submit your work':
        transition.set_permissions(MANAGER, conditions=(CHAIR, OWNER_CALL_OPEN), reset=True)
    elif transition.name == 'redraft':
        transition.set_permissions(MANAGER, conditions=(CHAIR, OWNER_CALL_OPEN), reset=True)
    elif transition.name == 'send to reviewer':
        transition.set_permissions(MANAGER, conditions=CHAIR, reset=True)
    elif transition.name == 'need correction':
        transition.set_permissions(MANAGER, conditions=(REVIEWER,CHAIR), reset=True)
    elif transition.name == 'resend to reviewer':
        transition.set_permissions(OWNER_MANAGER, conditions=CHAIR, reset=True)
    elif transition.name == 'accept talk':
        transition.set_permissions(MANAGER, conditions=(REVIEWER,CHAIR), reset=True)
    elif transition.name == 'reject talk':
        transition.set_permissions(MANAGER, conditions=(REVIEWER,CHAIR), reset=True)
    else:
        raise Exception('unknown transition %s' % repr(transition.name))

commit()

sync_schema_props_perms()

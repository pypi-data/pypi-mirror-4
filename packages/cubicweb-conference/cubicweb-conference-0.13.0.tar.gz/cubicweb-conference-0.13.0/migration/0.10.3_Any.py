### Redefinition of the workflows permissions

# see postcreate.py
CONF_CHAIR = 'U is_chair_at X'
TALK_CHAIR = 'U is_chair_at C, X in_conf C, X is Talk'
REVIEWER = 'U is_reviewer_at C, X in_conf C'
OWNER_CALL_OPEN = 'X owned_by U, X in_conf C, C call_open True'
MANAGER = ('managers',)
OWNER_MANAGER = ('owners', 'managers')

def set_workflow_permissions(perms):
    for name, permissions in perms.items():
        requiredgroups, conditions = permissions
        tr = rql('Transition T WHERE T name %(name)s', {'name': name})
        assert len(tr)==1
        tr = tr.entities().next()
        tr.set_permissions(requiredgroups, conditions, reset=True)

# Conference Workflow
redefine_conference_permissions = {
    'schedule':           (MANAGER,       CONF_CHAIR),
    'archive':            (MANAGER,       CONF_CHAIR),
}

# Talk Workflow
redefine_talk_permissions = {
    'submit your work':   (MANAGER,       (TALK_CHAIR, OWNER_CALL_OPEN) ),
    'redraft':            (MANAGER,       (TALK_CHAIR, OWNER_CALL_OPEN) ),
    'send to reviewer':   (MANAGER,       (TALK_CHAIR,)                 ),
    'need correction':    (MANAGER,       (REVIEWER, TALK_CHAIR)        ),
    'resend to reviewer': (OWNER_MANAGER, (TALK_CHAIR,)                 ),
    'propose to accept':  (MANAGER,       (REVIEWER, TALK_CHAIR)        ),
    'propose to reject':  (MANAGER,       (REVIEWER, TALK_CHAIR)        ),
    'need more review':   (MANAGER,       (REVIEWER, TALK_CHAIR)        ),
    'accept talk':        (MANAGER,       (TALK_CHAIR,)                 ),
    'reject talk':        (MANAGER,       (TALK_CHAIR,)                 ),
}

set_workflow_permissions(redefine_conference_permissions)
set_workflow_permissions(redefine_talk_permissions)
commit()

add_cube('forgotpwd')

# add_entity_type('Sponsor', auto=True) not necessary, add_cube above is greedy

set_property('actions.about.visible', u'')
set_property('actions.changelog.visible', u'')
set_property('boxes.blog_summary_box.visible', u'')

# change talk workflow

talk_states = rql('Any T, N ORDERBY T WHERE T in_state S, S name N, T is Talk').rows

rql('DELETE Workflow WF WHERE WF workflow_of X, X name "Talk"')

def define_talk_workflow():
    twf = add_workflow(_('talk workflow'), 'Talk')
    draft = twf.add_state(_('draft'), initial=True)
    submitted = twf.add_state(_('submitted'))
    correction = twf.add_state(_('correction'))
    inreview = twf.add_state(_('inreview'))
    accepted = twf.add_state(_('accepted'))
    rejected = twf.add_state(_('rejected'))
    twf.add_transition(_('submit your work'), (draft,), submitted,
                       ('owners',))
    twf.add_transition(_('send to reviewer'), (submitted,), inreview,
                       ('managers',))
    twf.add_transition(_('ask for correction'), (inreview,), correction,
                       ('managers',), conditions=('U reviews X',))
    twf.add_transition(_('submit your work'), (correction,), inreview,
                       ('owners',))
    twf.add_transition(_('accept talk'), (inreview,), accepted,
                       ('managers',), conditions=('U reviews X',))
    twf.add_transition(_('reject talk'), (inreview,), rejected,
                       ('managers',), conditions=('U reviews X',))

define_talk_workflow()

urql = session.unsafe_execute

for ent, name in talk_states:
    if name not in ('accepted', 'rejected'):
        name = _('draft')
    urql('SET X in_state S WHERE X eid %(x)s, S name %(name)s, X is ET, '
         'ET default_workflow WF, S state_of WF, WF workflow_of T, '
         'T name "Talk"', {'x': ent, 'name': name}, 'x')

commit()

sync_schema_props_perms()

commit()

# rename a transition, then allow managers to pass two transitions
rql('SET T name "resend to reviewer" WHERE T is Transition, T name "submit your work", '
    'T transition_of W, W workflow_of X, X name "Talk", S allowed_transition T, S name "correction"')
rset = rql('Any T WHERE T is Transition, T name "submit your work", '
           'T transition_of W, W workflow_of X, X name "Talk"')
transition = rset.get_entity(0,0)
transition.set_permissions(requiredgroups=('managers',), reset=False)
rset = rql('Any T WHERE T is Transition, T name "resend to reviewer", '
           'T transition_of W, W workflow_of X, X name "Talk"')
transition = rset.get_entity(0,0)
transition.set_permissions(requiredgroups=('managers',), reset=False)

commit()

# change cardinality of relation 'leads' and maxsize of Talk.title
sync_schema_props_perms()


from cubicweb.web.action import Action, LinkToEntityAction
from cubicweb.web.views import actions
from cubicweb.selectors import (
    one_line_rset, has_permission, is_instance, match_user_groups,
    rql_condition, match_search_state, partial_relation_possible)

# don't add action to add a talk in uicfg
# (actionbox_appearsin_addmenu) because these actions must be display
# only for managers, users have a specific button (confCallForPaper)
# to add a talk
class AddTalkInConferenceAction(LinkToEntityAction):
    __regid__ = 'addtalkinconf'
    __select__ = (match_search_state('normal') & one_line_rset()
                  & partial_relation_possible(action='add', strict=False)
                  & is_instance('Conference')
                  & (match_user_groups('managers') | rql_condition('U is_chair_at X')))

    title = _('add Talk in_conf Conference object')
    target_etype = 'Talk'
    rtype = 'in_conf'
    role = 'object'

class AddTalkInTrackAction(LinkToEntityAction):
    __regid__ = 'addtalkintrack'
    __select__ = (match_search_state('normal') & one_line_rset()
                  & partial_relation_possible(action='add', strict=False)
                  & is_instance('Track')
                  & (match_user_groups('managers')
                     | rql_condition('U is_chair_at C, X is Track, X in_conf C'))
                 )

    title = _('add Talk in_track Track object')
    target_etype = 'Talk'
    rtype = 'in_track'
    role = 'object'

class ModifyAction(actions.ModifyAction):
    # remove has_permission('update') from __select__
    # indeed user can set "attend" relation to a talk
    # but this action is done with a specific button
    # in the talk primary view
    # we want to see the modify action only if user can
    # update the entity
    __select__ = (Action.__select__ & one_line_rset() &
                  has_permission('update'))

def registration_callback(vreg):
    vreg.unregister(actions.CopyAction)
    vreg.register_and_replace(ModifyAction, actions.ModifyAction)
    for entity in (AddTalkInConferenceAction, AddTalkInTrackAction):
        vreg.register(entity)

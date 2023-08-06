from cubicweb.web import formfields as ff, formwidgets as fwdgs
from cubicweb.web.views.workflow import (WFHistoryVComponent, ChangeStateFormView)
from cubicweb.selectors import (match_user_groups, rql_condition, is_instance)
from cubes.conference.views.forms import reviewers_vocabulary

class ConferenceWFHistoryVComponent(WFHistoryVComponent):
    __select__ = (WFHistoryVComponent.__select__ & is_instance('Talk') &
                  (match_user_groups('owners', 'managers')
                   | rql_condition('U reviews X')
                   | rql_condition('U is_chair_at C, X is Talk, X in_conf C')))


class SendToReviewerStatusChangeView(ChangeStateFormView):
    __select__ = (ChangeStateFormView.__select__ &
                  is_instance('Talk') & match_user_groups('managers') &
                  rql_condition('X in_state S, S name "submitted"'))

    def get_form(self, entity, transition, **kwargs):
        # XXX used to specify both rset/row/col and entity in case implements
        # selector (and not implements) is used on custom form
        form = self._cw.vreg['forms'].select(
            'changestate', self._cw, entity=entity, transition=transition,
            redirect_path=self.redirectpath(entity), **kwargs)

        relation = ff.RelationField(name='reviews', role='object',
                                    eidparam=True,
                                    label=_('select reviewers'),
                                    widget=fwdgs.Select(multiple=True),
                                    choices=reviewers_vocabulary)
        form.append_field(relation)
        trinfo = self._cw.vreg['etypes'].etype_class('TrInfo')(self._cw)
        trinfo.eid = self._cw.varmaker.next()
        subform = self._cw.vreg['forms'].select('edition', self._cw, entity=trinfo,
                                                mainform=False)
        subform.field_by_name('wf_info_for', 'subject').value = entity.eid
        trfield = subform.field_by_name('by_transition', 'subject')
        trfield.widget = fwdgs.HiddenInput()
        trfield.value = transition.eid
        form.add_subform(subform)
        return form

def registration_callback(vreg):
    vreg.register(SendToReviewerStatusChangeView)
    vreg.register_and_replace(ConferenceWFHistoryVComponent, WFHistoryVComponent)

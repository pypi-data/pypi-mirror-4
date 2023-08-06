from cubicweb.web import component
from cubicweb.selectors import is_instance, match_user_groups, rql_condition

class TalkStateCtxComponent(component.EntityCtxComponent):
    __regid__ = 'talkstate'
    __select__ = (component.EntityCtxComponent.__select__
                  & is_instance('Talk') & match_user_groups('owners'))
    context = 'navcontenttop'

    def init_rendering(self):
        _cw = self._cw
        state = self.entity.cw_adapt_to('IWorkflowable').state
        color_action = _cw.uiprops.get('workflowColorAction')
        color_wait = _cw.uiprops.get('workflowColorWait')
        if state in ('draft', 'correction'):
            self.msg = (_cw._(u'This talk is in state "%s", which means it needs to be '
                              'submitted before it can be considered by the reviewers.')
                        % _cw._(state))
            self.color = color_action
        elif state in ('submitted', 'inreview'):
            self.msg = (_cw._(u'This talk is in state "%s", which means the reviewers '
                              'will soon send you their comments.')
                        % _cw._(state))
            self.color = color_wait
        elif state in ('accept_pending', 'reject_pending'):
            self.msg = _cw._(u'This talk was reviewed and is now awaiting a final '
                             'decision by the conference chairs.')
            self.color = color_wait
        else:
            raise component.EmptyComponent()

    def render_body(self, w):
        w(u'<div style="background-color: %s">' % self.color)
        w(self.msg)
        w(u'</div>')

class TalkStateCtxComponent2(TalkStateCtxComponent):
    __regid__ = 'talkstate2'
    __select__ = (component.EntityCtxComponent.__select__
                  & is_instance('Talk') & rql_condition('U reviews X'))

    def init_rendering(self):
        _cw = self._cw
        state = self.entity.cw_adapt_to('IWorkflowable').state
        color_action = _cw.uiprops.get('workflowColorAction')
        color_wait = _cw.uiprops.get('workflowColorWait')
        if state == 'inreview':
            self.msg = (_cw._(u'This talk is in state "%s", which means you have '
                              'to review it. You can ask the author for modifications, '
                              'accept or reject this talk.')
                        % _cw._(state))
            self.color = color_action
        elif state == 'correction':
            self.msg = (_cw._(u'This talk is in state "%s", which means the author '
                              'needs to answer the comments of the reviewers.')
                        % _cw._(state))
            self.color = color_wait
        elif state in ('accept_pending', 'reject_pending'):
            self.msg = _cw._(u'This talk was reviewed and is now awaiting a final '
                             'decision by the conference chairs.')
            self.color = color_wait
        else:
            raise component.EmptyComponent()


_ = unicode

from cubicweb.web import Redirect
from cubicweb.view import StartupView
from cubicweb.web.views import startup

from logilab.mtconverter import xml_escape

REPLACE = []

# index view
class ConferenceIndexView(startup.IndexView):
    __regid__ = 'index'
    title = _('Index')
    add_etype_links = ('Conference',)
    upcoming_conferences = ('Any C ORDERBY S DESC WHERE C is Conference, C start_on S, C end_on >= now')
    past_conferences = ('Any C ORDERBY S DESC WHERE C is Conference, C start_on S, C end_on < now')

    def call(self):
        rset = self._cw.execute('Any X WHERE X wikiid "indexpage"')
        if rset:
            entity = rset.get_entity(0,0)
            content = entity.printable_value('content', format='text/html')
            self.w(u'<div id="indexpage">')
            self.w(content)
            self.w(u'</div>')
        rset_next = self._cw.execute(self.upcoming_conferences)
        if rset_next:
            self.w(u'<h2>%s</h2>' % self._cw._(u'Upcoming conferences'))
            self.w(u'<ul>')
            for conf in rset_next.entities():
                self.w(u'<li>%s</li>' % conf.view('outofcontext'))
            self.w(u'</ul>')
        rset_past = self._cw.execute(self.past_conferences)
        if rset_past:
            self.w(u'<h2>%s</h2>' % self._cw._(u'Past conferences'))
            self.w(u'<ul>')
            for conf in rset_past.entities():
                self.w(u'<li>%s</li>' % conf.view('outofcontext'))
            self.w(u'</ul>')
        if not rset_next and not rset_past:
            self.w(self._cw._(u'No conference planned for now...'))

REPLACE.append( (ConferenceIndexView, startup.IndexView) )

# XXX move to cmt
class LoginOrRegister(StartupView):
    __regid__ = 'login_or_register'

    def call(self, title=True):
        redirpath = self._cw.form.get('__redirectpath')
        if self._cw.session.anonymous_session:
            if title:
                self.w(u'<h1>%s</h1>' % self._cw._(u'Authentication is needed to perform this action'))
            self.w(u'<h2>%s:</h2>' % self._cw._(u'If you already have an account, please log in'))
            form = self._cw.vreg['forms'].select('logform', self._cw, redirect_path=redirpath)
            self.w(form.render())
            self.w(u'<h2>%s:</h2>' % self._cw._(u'If you have an openid, please use it'))
            form = self._cw.vreg['forms'].select('openidlogform', self._cw)
            morebuttons = self._cw.vreg['buttons'].selectable('openid_button', self._cw)
            form.form_buttons = form.form_buttons[:]
            for button in morebuttons:
                form.form_buttons.insert(-1, button)
            self.w(form.render(display_progress_div=False))
            self.w(u'<h2>%s:</h2>' % self._cw._(u'If you do not have an account yet, please create one'))
            form = self._cw.vreg['forms'].select('registration', self._cw)
            self.w(form.render(display_progress_div=False))
        else:
            raise Redirect(self._cw.build_url(redirpath))
        # XXX would be even better to have a redirect message

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, [new for new,old in REPLACE])
    for new, old in REPLACE:
        vreg.register_and_replace(new, old)

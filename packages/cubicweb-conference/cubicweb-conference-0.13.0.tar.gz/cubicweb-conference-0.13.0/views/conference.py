from datetime import date

from logilab.mtconverter import xml_escape
from logilab.common.date import date_range, ONEDAY

from cubicweb.selectors import is_instance, rql_condition, match_user_groups
from cubicweb.view import EntityView
from cubicweb.web.views import tabs

_ = unicode

class ConferencePrimaryView(tabs.TabbedPrimaryView):
    __select__ = is_instance('Conference')
    tabs = [_('confinfo'), _('talkslist'), _('talksschedule'),
            _('userconfschedule'), _('adminview')]
    default_tab = 'confinfo'

    def render_entity_title(self, entity):
        self.w(u'<h1>%s</h1>' % entity.dc_long_title())


class ConferenceInfoView(EntityView):
    __select__ = is_instance('Conference')
    __regid__ = 'confinfo'

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        _ = self._cw._
        if entity.description:
            self.w(u'<div>%s</div>' % entity.dc_description('text/html'))
        rql = ('Any TR, TD, MIN(ST), MAX(ET), COUNT(T) GROUPBY TR, '
              'TD WHERE T? in_track TR, T start_time ST, T end_time ET, '
              'TR description TD, TR in_conf C, C eid %(c)s')
        rset = self._cw.execute(rql, {'c':entity.eid})
        if rset:
            if entity.end_on > date.today():
                text = _(u'The conference will be divided into the following tracks:')
            else:
                text = _(u'The conference was divided into the following tracks:')
            self.w(u'<div>%s</div>' % text)
            headers = (_(u'Track title'), _(u'Description'), _(u'First talk'),
                       _(u'Last talk'), _(u'Total talks'))
            self.wview('table', rset, headers=headers, displaycols=range(0,5))
        else:
            self.w(u'<div>%s</div>' % _(u'No track yet in this conference.'))

class UserConfSchedule(EntityView):
    __select__ = is_instance('Conference') & ~match_user_groups('guests')
    __regid__ = 'userconfschedule'

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        _ = self._cw._
        rql = ('Any T, ST, L ORDERBY ST WHERE T is Talk, T start_time ST, '
               'T location L, T in_conf C, C eid %(eid)s, U attend T, '
               'U login %(login)s')
        rset = self._cw.execute(rql, {'eid': entity.eid,
                                      'login': self._cw.user.login})
        if rset:
            self.w(u'<p>%s</p>' % _(u'You are planning to attend these talks:'))
            self.wview('table', rset, headers=(_(u'Talk title'),
                                               _(u'Date'), _(u'Location')))
        else:
            self.w(u'<p>%s</p>' % _(
                    u'Do you plan to attend a specific talk ? Please click on '
                    u'the attendancy button positionned at the top '
                    u'right of each talk summary.'))

class ConferenceTalksList(EntityView):
    __select__ = is_instance('Conference')
    __regid__ = 'talkslist'

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        _ = self._cw._
        rql = ('Any T, group_concat(U), ST, L, TR GROUPBY T, ST, L, TR '
               'ORDERBY ST WHERE T location L, T start_time ST, '
               'U leads T, T in_conf C, T in_track TR, T in_state S, T title TT, '
               'S name "accepted", C eid %(c)s')
        rset = self._cw.execute(rql, {'c': entity.eid})
        if rset:
            headers = (_(u'Talk title'), _(u'Speaker'), _(u'Date'),
                       _(u'Location'), _(u'Track'))
            self.wview('table', rset, headers=headers, cellvids={1:'users_list'})
        else:
            self.w(u'<div>%s</div>' % _(u'No accepted talk yet in this conference'))

class ConferenceTalksSchedule(EntityView):
    __select__ = is_instance('Conference') & rql_condition('T in_conf X')
    __regid__ = 'talksschedule'

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        tracks_rql = 'Any TR WHERE TR in_conf C, TR is Track, C eid %(c)s'
        tracks = list(self._cw.execute(tracks_rql, {'c': entity.eid}).entities())
        for day in date_range(entity.start_on, entity.end_on+ONEDAY):
            self.w(u'<table style="width:100%">')
            self.w(u'<tr>')
            for track in tracks:
                if entity.has_talk(day, track):
                    rset = self._cw.execute('Any T WHERE T in_track TR, TR eid %(e)s, '
                                            'T in_state S, S name "accepted"', {'e': track.eid})
                    if rset:
                        self.w(u'<td>')
                        self.wview('onedaycal', rset, initargs={'day':day, 'title':track.title})
                        self.w(u'</td>')
            self.w(u'</tr></table>')

class ConferenceAdminView(EntityView):
    __select__ = is_instance('Conference') & (match_user_groups('managers')
                                              | rql_condition('U is_chair_at X'))
    __regid__ = 'adminview'

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(0,0)
        # number of talks in each state
        self.w(u'<h2>%s</h2>' % self._cw._(u'Talk state details'))
        entity = self.cw_rset.get_entity(0,0)
        rql = 'Any S, COUNT(T) GROUPBY S WHERE T is Talk, T in_state S, T in_conf C, C eid %(eid)s'
        rset = self._cw.execute(rql, {'eid': entity.eid})
        self.wview('table', rset, 'null')
        rset = self._cw.execute('Any T WHERE T is Talk, T in_state S, S name "submitted"')
        if rset:
            treid = self._cw.execute('Any T WHERE T is Transition, T name "send to reviewer"')[0][0]
            self.w(u'<div id="statreview">')
            self.w(u'<p>%s</p>' % self._cw._(u'Please, assign a reviewer to :'))
            self.w(u'<ul>')
            for talk in rset.entities():
                self.w('<li><a href="%s">%s</a></li>' %
                       (xml_escape(talk.absolute_url(vid='statuschange', treid=treid)),
                        xml_escape(talk.title)))
            self.w(u'</ul></div>')
        # number of participant by talk
        self.w(u'<h2>%s</h2>' % self._cw._(u'Number of participant by Talk'))
        rql = 'Any T, COUNT(A) GROUPBY T WHERE T is Talk, A attend T, T in_conf C, C eid %(eid)s'
        rset = self._cw.execute(rql, {'eid': entity.eid})
        self.wview('table', rset, 'null')


"""this contains the template-specific entities' classes"""

__docformat__ = "restructuredtext en"

from logilab.common.date import todate

from cubicweb.selectors import is_instance
from cubicweb.entities import AnyEntity, adapters, fetch_config
from cubicweb.entities.authobjs import CWUser
from cubicweb.web.views.calendar import ICalendarableAdapter
from cubicweb.web.views.ibreadcrumbs import IBreadCrumbsAdapter
from cubicweb.view import EntityAdapter

# cwuser

class ConferenceCWUser(CWUser):

    def dc_long_title(self):
        name = super(ConferenceCWUser, self).name()
        if self.representing:
            return u'%s (%s)' % (name, self.representing)
        else:
            return name

# conference

class Conference(AnyEntity):
    __regid__ = 'Conference'

    rest_attr = 'url_id'

    def dc_long_title(self):
        if self.start_on.month == self.end_on.month:
            dates = u'%s %s-%s' % (self.start_on.strftime('%B'), self.start_on.day, self.end_on.day)
        else:
            dates = u'%s - %s' % (self.start_on.strftime('%B %d'), self.end_on.strftime('%B %d'))
        city = self.take_place_at[0].city
        return u'%s - %s %s' % (self.title, dates, city)

    def get_talks_by_track(self, track):
        rql = 'Any T WHERE T in_track TR, TR eid %(tr)s'
        return self._cw.execute(rql, {'tr': track.eid})

    def has_talk(self, day, track):
        for talk in self.get_talks_by_track(track).entities():
            if talk.is_on_day(day):
                return True
        return False

class ConferenceITreeAdapter(adapters.ITreeAdapter):
    __select__ = is_instance('Conference')

    tree_relation = 'in_conf'

class ConferenceIBreadCrumbsAdapter(IBreadCrumbsAdapter):
    __select__ = is_instance('Conference')

    def breadcrumbs(self, view=None, recurs=False):
        return [(self.entity.absolute_url(), self.entity.dc_title())]

# track

class Track(AnyEntity):
    __regid__ = 'Track'
    fetch_attrs, fetch_order = fetch_config(['title'])

class TrackICalendarableAdapter(ICalendarableAdapter):
    __select__ = is_instance('Track')

    @property
    def start(self):
        rql_date = ("Any MIN(ST) WHERE T eid %(track)s, X in_track T,"
                    "X start_time ST, X in_state S, S name 'accepted'")
        rset = self._cw.execute(rql_date, {"track": self.entity.eid})
        # Aggregate function can return None (#1381429)
        if len(rset) and rset[0][0] is not None:
            return rset[0][0]

    @property
    def stop(self):
        rql_date = ("Any MAX(ET) WHERE T eid %(track)s, X in_track T,"
                    "X end_time ET, X in_state S, S name 'accepted'")
        rset = self._cw.execute(rql_date, {"track": self.entity.eid})
        # Aggregate function can return None (#1381429)
        if len(rset) and rset[0][0] is not None:
            return rset[0][0]

class TrackITreeAdapter(adapters.ITreeAdapter):
    __select__ = is_instance('Track')

    tree_relation = 'in_track'

class TrackIBreadCrumbsAdapter(IBreadCrumbsAdapter):
    __select__ = is_instance('Track')

    def breadcrumbs(self, view=None, recurs=False):
        breadcrumbs = []
        if self.entity.in_conf:
            breadcrumbs = self.entity.in_conf[0].cw_adapt_to('IBreadCrumbs').breadcrumbs(view, True)
        breadcrumbs.append(self.entity)
        return breadcrumbs

# talk

class Talk(AnyEntity):
    __regid__ = 'Talk'
    fetch_attrs, fetch_order = fetch_config(['start_time', 'end_time'])

    def is_on_day(self, day):
        date = todate(day)
        if self.start_time:
            talk_date = todate(self.start_time)
            return date == talk_date
        else:
            return False

    @property
    def track(self):
        # track is not mandatory in schema by default
        if self.in_track:
            return self.in_track[0]


class TalkIBreadCrumbsAdapter(IBreadCrumbsAdapter):
    __select__ = is_instance('Talk')

    def breadcrumbs(self, view=None, recurs=False):
        try:
            breadcrumbs = self.entity.in_track[0].cw_adapt_to('IBreadCrumbs').breadcrumbs(view, True)
        except IndexError:
            breadcrumbs = []
        breadcrumbs.append(self.entity)
        return breadcrumbs

class TalkICalendarableAdapter(EntityAdapter):
    __regid__ = 'ICalendarable'
    __select__ = is_instance('Talk')

    @property
    def start(self):
        return self.entity.start_time

    @property
    def stop(self):
        return self.entity.end_time

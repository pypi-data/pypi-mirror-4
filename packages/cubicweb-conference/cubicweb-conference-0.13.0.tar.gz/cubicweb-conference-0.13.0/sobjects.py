import datetime

from cubicweb.appobject import objectify_selector
from cubicweb.selectors import is_instance
from cubicweb.server.hook import Hook, match_rtype
from cubicweb.sobjects.notification import (
    RecipientsFinder, NotificationView, StatusChangeMixIn)

from cubes.conference.utils import normalize_name


def get_unique_url_id(execute, conference):
    url_id = normalize_name(conference.title)
    suffix = 0
    new_url_id = url_id
    while True:
        rset = execute('Any C WHERE C url_id %(url)s',
                       {'url': new_url_id})
        if not rset:
            return new_url_id
        suffix += 1
        new_url_id = '%s_%s' % (url_id, suffix)


class ConferenceUrlIdentifierHook(Hook):
    """
    If the conference has no url_id attribute, generate it automatically.
    """
    __regid__ = 'conference-url-identifier-hook'
    __select__ = Hook.__select__ & is_instance('Conference')
    events = ('before_add_entity',)

    def __call__(self):
        if not self.entity.url_id:
            url_id = get_unique_url_id(self._cw.execute, self.entity)
            self.entity.cw_edited['url_id'] = url_id

class AddTalkLeadHook(Hook):
    __regid__ = 'add-talk-lead-hook'
    __select__ = is_instance('Talk')
    events = ('after_add_entity',)

    def __call__(self):
        if not self._cw.is_internal_session:
            asession = self._cw
            asession.execute('SET U leads X WHERE X eid %(x)s, U eid %(u)s, NOT U attend X',
                             {'x': self.entity.eid, 'u': self._cw.user.eid})

class LeadsHook(Hook):
    """
    Create relation attend on CWUser who leads a Talk:
    U leads T => U attend T
    """
    __regid__ = 'lead-entails-attend-hook'
    __select__ = Hook.__select__ & match_rtype('leads')
    events = ('after_add_relation',)

    def __call__(self):
        if not self._cw.is_internal_session:
            asession = self._cw
            asession.execute('SET U attend X WHERE X eid %(x)s, U eid %(u)s, NOT U attend X',
                             {'x': self.eidto, 'u': self.eidfrom})

class InTrackHook(Hook):
    """
    When a Talk is added to a Track, automatically add it to the Conference:
    T in_track TR => T in_conf C
    """
    __regid__ = 'in_track-entails-in_conf-hook'
    __select__ = Hook.__select__ & match_rtype('in_track')
    events = ('before_add_relation',)

    def __call__(self):
        if not self._cw.is_internal_session:
            asession = self._cw
            rql = 'Any C WHERE TR in_conf C, TR eid %(tr)s'
            conf = asession.execute(rql, {'tr': self.eidto})
            asession.execute('SET T in_conf C WHERE T eid %(t)s, C eid %(c)s, NOT T in_conf C',
                             {'t': self.eidfrom, 'c': conf[0][0]})

class InConfHook(Hook):
    """
    Remove already existing relation X in_conf C when trying to add a new
    relation X in_conf C
    """
    __regid__ = 'switch-in_conf-hook'
    __select__ = Hook.__select__ & match_rtype('in_conf')
    events = ('before_add_relation',)

    def __call__(self):
         if not self._cw.is_internal_session:
            asession = self._cw
            rql = 'Any C WHERE X in_conf C, X eid %(x)s'
            conf = asession.execute(rql, {'x': self.eidfrom})
            if conf:
                asession.execute('DELETE X in_conf C WHERE X eid %(x)s, C eid %(c)s',
                                 {'x': self.eidfrom, 'c': conf[0][0]})


#-------------------
# Email notification
#-------------------

class TalkNotificationView(NotificationView):
    __select__ = NotificationView.__select__ & is_instance('Talk',)

    def context(self, **kwargs):
        context = super(TalkNotificationView, self).context(**kwargs)
        entity = self.cw_rset.complete_entity(0,0)
        context.update({'talk_name': entity.title,
                        'date': datetime.date.today().isoformat(),
                        'firstname': entity.reverse_leads[0].firstname,
                        'lastname': entity.reverse_leads[0].surname,
                        'conference': entity.in_track[0].in_conf[0].title})
        return context

    def recipients(self):
        recipients = []
        for finderid in self.recipients_finder:
            finder = self._cw.vreg['components'].select(finderid, self._cw,
                                                        rset= self.cw_rset)
            recipients += finder.recipients()
        return recipients

class TalkAddRecipientsFinder(RecipientsFinder):
    __select__ = RecipientsFinder.__select__ & is_instance('Talk',)
    __regid__ = 'manager_finder'

    @property
    def user_rql(self):
        return ('Any U, E, A WHERE U is CWUser, U in_group N, N name "managers", U primary_email E, E address A')

class TalkUpdateRecipientsFinder(RecipientsFinder):
    __select__ = RecipientsFinder.__select__ & is_instance('Talk',)
    __regid__ = 'interested_by_finder'

    @property
    def user_rql(self):
        return ('Any U, E, A WHERE X eid %(eid)s, EXISTS(U reviews X) '
                'OR EXISTS(U leads X), U primary_email E, E address A' %
                {'eid':  self.cw_rset[0][0]})

class TalkAdd(TalkNotificationView):
    """  Send an email to managers after a talk creation
    """
    __regid__ = 'notif_after_add_entity'

    recipients_finder = ('manager_finder',)

    content = _(u""
                u"Dear %(firstname)s %(lastname)s,\n"
                u"\n"
                u"The talk '%(talk_name)s' was added on %(date)s.\n"
                u"\n"
                u"Sincerely,\n"
                u"\n"
                u"--\n"
                u"The %(conference)s organizing committee.\n")

    def subject(self):
        entity = self.cw_rset.get_entity(0,0)
        return self._cw._('[%s] a talk was added') % entity.in_track[0].in_conf[0].title

# XXX move to framework ?
# XXX why metaattrsupdate is updated at before_update_entity ?
@objectify_selector
def entity_really_edited(cls, req, rset=None, **kwargs):
    # when the status of an entity changes, the modification_date of the entity changes too
    # in case of talks, don't call talkupdate if only modification_date attribute has changed
    entity = rset.get_entity(0, 0)
    if len(entity.cw_edited) == 1 and 'modification_date' in entity.cw_edited:
        return 0
    return 1

class TalkUpdate(TalkNotificationView):
    __regid__ = 'notif_after_update_entity'
    recipients_finder = ('manager_finder', 'interested_by_finder',)
    __select__ = TalkNotificationView.__select__ & entity_really_edited()

    content = _(u""
                u"Dear %(firstname)s %(lastname)s,\n"
                u"\n"
                u"The talk '%(talk_name)s' was modified on %(date)s.\n"
                u"\n"
                u"Sincerely,\n"
                u"\n"
                u"--\n"
                u"The %(conference)s organizing committee.\n")

    def subject(self):
        entity = self.cw_rset.get_entity(0,0)
        return self._cw._('[%s] a talk was updated') % entity.in_track[0].in_conf[0].title

class TalkStatusUpdate(StatusChangeMixIn, TalkNotificationView):
    recipients_finder = ('manager_finder', 'interested_by_finder')

    content = _(u""
                u"Dear user,\n\n"
                u"The '%(title)s' status was updated from '%(previous_state)s' to '%(current_state)s'.\n\n"
                u"Sincerely,\n"
                u"\n"
                u"--\n"
                u"The conference organizing committee.\n")

    def subject(self):
        entity = self.cw_rset.get_entity(0,0)
        return _(u'[%s] talk status was updated' % entity.in_track[0].in_conf[0].title)

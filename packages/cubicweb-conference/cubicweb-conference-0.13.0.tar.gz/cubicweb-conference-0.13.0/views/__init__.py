from logilab.mtconverter import xml_escape

from cubicweb.view import View
from cubicweb.selectors import is_instance, match_user_groups
from cubicweb.web.views import primary
from cubicweb.web import uicfg
from cubes.conference.views.forms import (subject_in_track_vocabulary,
                                          subject_call_open_conf_vocabulary)

from cubicweb.web.views.basetemplates import HTMLPageHeader
HTMLPageHeader.headers = (('header-left', 'header-left'),
                          ('headtext', 'header-center'),
                          ('header-right', 'header-right'),
                         )

from cubicweb.web.views.basecomponents import ApplicationName
from cubicweb.web.views.ibreadcrumbs import BreadCrumbEntityVComponent
ApplicationName.context = BreadCrumbEntityVComponent.context = 'header-center'

_pvs = uicfg.primaryview_section
_pvs.tag_subject_of(('Talk', 'has_attachments', 'File'), 'hidden')
_pvs.tag_object_of(('CWUser', 'leads', 'Talk'), 'hidden')
_pvs.tag_object_of(('*', 'in_conf', '*'), 'hidden')
_pvs.tag_subject_of(('*', 'in_conf', '*'), 'hidden')
_pvs.tag_subject_of(('Talk', 'in_track', '*'), 'hidden')
_pvs.tag_object_of(('Talk', 'in_track', '*'), 'hidden')
_pvs.tag_subject_of(('CWUser', 'attend', '*'), 'hidden')
_pvs.tag_object_of(('CWUser', 'reviews', 'Talk'), 'hidden')
_pvs.tag_object_of(('*', 'attend', 'Talk'), 'hidden')
_pvs.tag_object_of(('Conference', 'take_place_at', 'PostalAddress'), 'relations')

_abaa = uicfg.actionbox_appearsin_addmenu
_abaa.tag_subject_of(('Talk', 'has_attachments', 'File'), True)
_abaa.tag_object_of(('Track', 'in_conf', 'Conference'), True)
_abaa.tag_object_of(('Talk', 'in_conf', 'Conference'), False)
_abaa.tag_object_of(('Talk', 'in_track', 'Track'), False)

_afs = uicfg.autoform_section
_afs.tag_object_of(('CWUser', 'leads', 'Talk'), formtype='main', section='hidden')
_afs.tag_subject_of(('Sponsor', 'has_logo', '*'), formtype='main', section='inlined')
_afs.tag_subject_of(('Talk', 'in_track', '*'), formtype='main', section='attributes')
_afs.tag_subject_of(('Conference', 'take_place_at', 'PostalAddress'), formtype="main", section="inlined")
_afs.tag_attribute(('PostalAddress', 'latitude'), formtype="main", section="attributes")
_afs.tag_attribute(('PostalAddress', 'longitude'), formtype="main", section="attributes")

uicfg.autoform_field_kwargs.tag_subject_of(('Talk', 'in_track', 'Track'),
                                           {'choices': subject_in_track_vocabulary})
uicfg.autoform_field_kwargs.tag_subject_of(('Talk', 'in_conf', 'Conference'),
                                           {'choices': subject_call_open_conf_vocabulary})
uicfg.autoform_field_kwargs.tag_subject_of(('Talk', 'has_attachments', 'File'),
                                           {'order': -1})

class UsersList(View):
    __regid__ = 'users_list'

    def cell_call(self, row, col):
        user_eids = self.cw_rset[row][col].split(',')
        users = []
        for user_eid in user_eids:
            rset = self._cw.execute('Any U WHERE U eid %(e)s', {'e': user_eid})
            users.append(rset.get_entity(0,0).dc_long_title())
        self.w(', '.join(users))


class CWUserPrimaryView(primary.PrimaryView):
    __select__ = is_instance('CWUser') & match_user_groups('guests')

    def render_entity_title(self, entity):
        title = xml_escape(entity.dc_long_title())
        self.w(u'<h1>%s</h1>' % title)

    def render_entity_attributes(self, entity):
        if entity.representing:
            self.w("%s %s" % (self._cw._(u'Representing'), entity.representing))

from cubicweb.web.views.urlrewrite import SimpleReqRewriter, rgx

class ConferenceTabRewrite(SimpleReqRewriter):
    rules = [
        (rgx('/conference/([^/]+)/([A-Za-z]+)'),
         dict(rql='Any C WHERE C is Conference, C url_id "%(id)s"' % {'id': r'\1'},
              selected_tab=r'\2', tab=r'\2')),
         ]

from cubes.seo.views import SitemapRule

class ConferenceSitemapRule(SitemapRule):
    __regid__ = 'conference'
    query = 'Any X WHERE X is Conference'
    priority = 1.0
    chfreq = 'monthly'

class TrackSitemapRule(SitemapRule):
    __regid__ = 'track'
    query = 'Any X WHERE X is Track'
    priority = 1.0
    chfreq = 'monthly'

class TalkSitemapRule(SitemapRule):
    __regid__ = 'talk'
    query = 'Any X WHERE X is Talk'
    priority = 1.0
    chfreq = 'monthly'


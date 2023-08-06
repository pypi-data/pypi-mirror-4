from cubicweb.selectors import is_instance
from cubicweb.web.facet import RelationFacet, DateRangeFacet

# This selector is used by the TalkDate facet,
# the start_time date is optional.

class TalkDateFacet(DateRangeFacet):
    __regid__ = 'date-facet'
    __select__ = DateRangeFacet.__select__ & is_instance('Talk')
    rtype = 'start_time'

    @property
    def title(self):
        return self._cw._("Date")

class TalkTrackFacet(RelationFacet):
    __regid__ = 'track-facet'
    __select__ = RelationFacet.__select__ & is_instance('Talk')
    rtype = 'in_track'
    target_attr = 'title'

class TalkTagsFacet(RelationFacet):
    __regid__ = 'tags-facet'
    __select__ = RelationFacet.__select__ & is_instance('Talk')
    rtype = 'tags'
    target_attr = 'name'

class TalkConferenceFacet(RelationFacet):
    __regid__ = 'conference-facet'
    __select__ = RelationFacet.__select__ & is_instance('Talk')
    rtype = 'in_conf'
    target_attr = 'title'

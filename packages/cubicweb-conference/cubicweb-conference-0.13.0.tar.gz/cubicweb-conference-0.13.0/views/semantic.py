from logilab.mtconverter import xml_escape

from cubicweb.view import EntityView
from cubicweb.selectors import is_instance, one_line_rset

class SwcConferenceView(EntityView):
    __regid__ = 'swc'
    __select__ = is_instance('Conference') & one_line_rset()
    title = _('swc')
    templatable = False
    content_type = 'application/rdf+xml'

    def call(self):
        self.w(u'''<?xml version="1.0" encoding="%s"?>
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:rdfs="http://www.w3org/2000/01/rdf-schema#"
        xmlns:swrc="http://swrc.ontoware.org/ontology#"
        xmlns:swc="http://data.semanticweb.org/ns/swc/ontology#"
        xmlns:foaf="http://xmlns.com/foaf/0.1/"
        xmlns:dc="http://purl.org/dc/elements/1.1/#"
        xmlns:ical="http://www.w3.org/2002/12/cal/ical#">\n''' % self._cw.encoding)
        self.cell_call(0, 0)
        self.w(u'</rdf:RDF>\n')

    def cell_call(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        self.w(u'<swc:ConferenceEvent rdf:about="%s">\n' % entity.absolute_url())
        self.w(u'<dc:title>%s</dc:title>\n' % xml_escape(entity.dc_title()))
        self.w(u'<rdfs:label>%s</rdfs:label>' % xml_escape(entity.dc_title()))
        self.w(u'<swc:hasAcronym>%s</swc:hasAcronym>' % xml_escape(entity.url_id))
        self.w(u'<ical:dtstart rdf:parseType="Resource">'
               u'<ical:date>%s</ical:date></ical:dtstart>' % entity.start_on)
        self.w(u'<ical:dtend rdf:parseType="Resource">'
               u'<ical:date>%s</ical:date></ical:dtend>' % entity.end_on)
        self.w(u'<ical:url rdf:resource="%s"/>' % entity.absolute_url())
        tracks = self._cw.execute('Any T WHERE T is Track, T in_conf C, C eid %(x)s',
                                  {'x': entity.eid}).entities()
        for track in tracks:
            self.w(u'<swrc:isSuperEventOf rdf:resource="%s"/>\n' % track.absolute_url())
        self.w(u'</swc:ConferenceEvent>\n')

class SwcTrackView(EntityView):
    __regid__ = 'swc'
    __select__ = is_instance('Track') & one_line_rset()
    title = _('swc')
    templatable = False
    content_type = 'application/rdf+xml'

    def call(self):
        self.w(u'''<?xml version="1.0" encoding="%s"?>
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:rdfs="http://www.w3org/2000/01/rdf-schema#"
        xmlns:swrc="http://swrc.ontoware.org/ontology#"
        xmlns:swc="http://data.semanticweb.org/ns/swc/ontology#"
        xmlns:foaf="http://xmlns.com/foaf/0.1/"
        xmlns:dc="http://purl.org/dc/elements/1.1/#">\n''' % self._cw.encoding)
        self.cell_call(0, 0)
        self.w(u'</rdf:RDF>\n')

    def cell_call(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        self.w(u'<swc:TrackEvent rdf:about="%s">' % entity.absolute_url())
        self.w(u'<dc:title>%s</dc:title>' % xml_escape(entity.dc_title()))
        for conf in entity.in_conf:
            self.w(u'<swc:isPartOf rdf:resource="%s"/>' % conf.absolute_url())
        for track in entity.reverse_in_track:
            self.w(u'<swrc:isSuperEventOf rdf:resource="%s"/>' % track.absolute_url())
        self.w(u'</swc:TrackEvent>')

class SwcTalkView(EntityView):
    __regid__ = 'swc'
    __select__ = is_instance('Talk')
    title = _('swc')
    templatable = False
    content_type = 'application/rdf+xml'

    def call(self):
        self.w(u'''<?xml version="1.0" encoding="%s"?>
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:rdfs="http://www.w3org/2000/01/rdf-schema#"
        xmlns:swrc="http://swrc.ontoware.org/ontology#"
        xmlns:swc="http://data.semanticweb.org/ns/swc/ontology#"
        xmlns:foaf="http://xmlns.com/foaf/0.1/"
        xmlns:dc="http://purl.org/dc/elements/1.1/#">\n''' % self._cw.encoding)
        for i in xrange(self.cw_rset.rowcount):
            self.cell_call(i, 0)
        self.w(u'</rdf:RDF>\n')

    def cell_call(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        self.w(u'<swc:TalkEvent rdf:about="%s">' % entity.absolute_url())
        for conf in entity.in_conf:
            self.w(u'<swc:isPartOf rdf:resource="%s"/>' % conf.absolute_url())
        for track in entity.in_track:
            self.w(u'<swc:isPartOf rdf:resource="%s"/>' % track.absolute_url())
        self.w(u'<dc:title>%s</dc:title>' % xml_escape(entity.dc_title()))
        self.w(u'<swrc:abstract><![CDATA[%s]]></swrc:abstract>' % entity.description)
        for author in entity.reverse_leads:
            self.w(u'<swrc:author rdf:resource="%s"/>' % author.absolute_url())
        for doc in entity.has_attachments:
            self.w(u'<swc:hasRelatedDocument rdf:resource="%s"/>' % doc.absolute_url())
        self.w(u'</swc:TalkEvent>')


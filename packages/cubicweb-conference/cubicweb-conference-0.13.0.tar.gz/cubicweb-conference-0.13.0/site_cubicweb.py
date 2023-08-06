from cubicweb.cwconfig import register_persistent_options

register_persistent_options((
    ('sponsor-contact-email',
     {'type' : 'string',
      'default': 'unset',
      'help': 'Sponsor contact email',
      'group': 'ui',
      'site_wide': True}),
     ))

from yams import xy

xy.register_prefix('swrc', 'http://swrc.ontoware.org/ontology')

xy.add_equivalence('Conference', 'swrc:ConferenceEvent')
xy.add_equivalence('CWUser login', 'foaf:name')
xy.add_equivalence('Talk', 'swrc:Paper')
xy.add_equivalence('Talk title', 'swrc:title')
xy.add_equivalence('Talk description', 'swrc:abstract')
xy.add_equivalence('Talk description', 'swrc:abstract')
xy.add_equivalence('Talk has_attachments', 'swrc:hasRelatedDocument')
xy.add_equivalence('Talk leads', 'swrc:author')

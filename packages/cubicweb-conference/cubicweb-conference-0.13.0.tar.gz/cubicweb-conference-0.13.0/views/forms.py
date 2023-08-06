from cubicweb.selectors import is_instance, match_user_groups
from cubicweb.web.views import autoform

# vocabulary for add / talk form

def reviewers_vocabulary(form, field):
    entity = form.edited_entity
    rset = form._cw.execute('Any U WHERE U is_reviewer_at C, X in_conf C, '
                            'X is Talk, X eid %(x)s', {'x': entity.eid})
    return [(item.dc_long_title(), item.eid) for item in rset.entities()]

def subject_call_open_conf_vocabulary(form, field):
    options = []
    edited_entity = form.edited_entity
    if edited_entity.has_eid() and edited_entity.in_conf:
        conf = edited_entity.in_conf[0]
        options = [(conf.dc_title(), conf.eid)]
    if form._cw.user.matching_groups('managers'):
        rset = form._cw.execute('Any C WHERE C is Conference')
    else:
        rset = form._cw.execute('Any C WHERE C is Conference, C call_open True, '
                                'C in_state S, S name "scheduled"')
    for entity in rset.entities():
        if edited_entity.has_eid() and conf.eid == entity.eid:
            continue
        options.append((entity.dc_title(), entity.eid))
    return options

def subject_reg_open_conf_vocabulary(form, field):
    options = []
    edited_entity = form.edited_entity
    if edited_entity.has_eid() and edited_entity.book_conf:
        conf = edited_entity.book_conf[0]
        options = [(conf.dc_title(), conf.eid)]
    if form._cw.user.matching_groups('managers'):
        rset = form._cw.execute('Any C WHERE C is Conference')
    else:
        rset = form._cw.execute('Any C WHERE C is Conference, C reg_open True, '
                                'C in_state S, S name "scheduled"')
    for entity in rset.entities():
        if edited_entity.has_eid() and conf.eid == entity.eid:
            continue
        options.append((entity.dc_title(), entity.eid))
    return options

def subject_in_track_vocabulary(form, field):
    options = []
    edited_entity = form.edited_entity
    if edited_entity.has_eid() and edited_entity.in_track:
        track = edited_entity.in_track[0]
        options = [(track.dc_title(), track.eid)]
    if form._cw.user.matching_groups('managers'):
        rset = form._cw.execute('Any T WHERE T is Track')
    else:
        rset = form._cw.execute('DISTINCT Any T WHERE T is Track, T in_conf C, '
                                'C call_open True, C in_state S, S name "scheduled"')
    for entity in rset.entities():
        if edited_entity.has_eid() and track.eid == entity.eid:
            continue
        options.append((entity.dc_title(), entity.eid))
    return options

class TalkAutoForm(autoform.AutomaticEntityForm):
    __select__ = autoform.AutomaticEntityForm.__select__ & is_instance('Talk') & match_user_groups('managers')

    def editable_relations(self):
        result = super(TalkAutoForm, self).editable_relations()
        rschema = self._cw.vreg.schema.rschema('leads')
        result.append( (rschema.display_name(self.edited_entity._cw, 'object', 'Talk'),
                        rschema, 'object') )
        return sorted(result)



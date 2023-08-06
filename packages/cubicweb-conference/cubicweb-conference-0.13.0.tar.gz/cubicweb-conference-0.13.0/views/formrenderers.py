from cubicweb.web.views.formrenderers import EntityFormRenderer
from cubicweb.selectors import match_user_groups

class UsersEntityFormRenderer(EntityFormRenderer):
    __select__ = EntityFormRenderer.__select__ & match_user_groups('users')

    def relations_form(self, w, form):
        return u''

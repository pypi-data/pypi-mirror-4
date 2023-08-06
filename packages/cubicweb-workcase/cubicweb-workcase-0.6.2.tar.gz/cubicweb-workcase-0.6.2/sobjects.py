"""this contains the server-side objects"""

from cubicweb import ValidationError
from cubicweb.selectors import is_instance
from cubicweb.server import hook

def check_wptitle(workcase, workpackage):
    """checks that `workpackage`'s title doesn't conflict with
    an existing workpackage in the same workcase
    """
    title = workpackage.title
    existing_wps = [wp.title for wp in workcase.split_into if wp is not workpackage]
    if title in existing_wps:
        msg = 'There is already a workpackage named %s in this workcase'
        raise ValidationError(workpackage.eid,
                              {'title': workpackage._cw._(msg) % title})


class BeforeAddSplitIntoRelation(hook.Hook):
    """checks that the new workpackage's title doesn't conflict with
    an existing workpackage in the same workcase
    """
    __regid__ = 'checkwptitle_on_splitinto_change'
    __select__ = hook.Hook.__select__ & hook.match_rtype('split_into')
    events = ('before_add_relation',)

    def __call__(self):
        check_wptitle(self._cw.entity_from_eid(self.eidfrom),
                      self._cw.entity_from_eid(self.eidto))


class CheckWPName(hook.Hook):
    """checks that the new workpackage's title doesn't conflict with
    an existing workpackage in the same workcase
    """
    __regid__ = 'checkwptitle_on_wp_update'
    __select__ = hook.Hook.__select__ & is_instance('Workpackage')
    events = ('before_update_entity',)

    def __call__(self):
        if 'title' in self.entity.cw_edited:
            # if the user hasn't updated/edited the title
            # it does not exist in the entity's dict-like interface
            check_wptitle(self.entity.reverse_split_into[0], self.entity)


"""template-specific forms/views/actions/components"""

from cubicweb.selectors import is_instance
from cubicweb.web import uicfg
from cubicweb.web.views import ibreadcrumbs

_abaa = uicfg.actionbox_appearsin_addmenu
_abaa.tag_subject_of(('Workcase', 'split_into', 'Workpackage'), True)
_abaa.tag_object_of(('Workcase', 'split_into', 'Workpackage'), False)


class WorkPackageIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('Workpackage')

    def parent_entity(self):
        parents = self.entity.reverse_split_into
        if parents:
            return parents[0]

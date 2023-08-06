"""this contains the template-specific entities' classes"""

from cubicweb.entities import AnyEntity, fetch_config

class Workcase(AnyEntity):
    __regid__ = 'Workcase'
    fetch_attrs, fetch_order = fetch_config(['ref', 'subject'])

    def dc_title(self):
        return self.ref.upper()

    def dc_long_title(self):
        return u'%s - %s' % (self.ref.upper(), self.subject)

    def dc_description(self, format='text/plain'):
        return self.printable_value('subject', format=format)


class WorkPackage(AnyEntity):
    __regid__ = 'Workpackage'
    fetch_attrs, fetch_order = fetch_config(['title'])

    def dc_title(self):
        return self.title

    def dc_long_title(self):
        ref = self.reverse_split_into[0].ref
        return u'%s - %s' % (ref, self.title)


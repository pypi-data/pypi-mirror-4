from cubicweb.selectors import is_instance
from cubicweb.web import uicfg
from cubicweb.web.views import ibreadcrumbs

_pvs = uicfg.primaryview_section
_pvs.tag_object_of(('Email', 'in_thread', 'EmailThread'), 'hidden')

# XXX fix cw.web.views.emailaddress.EmailAddressPrimaryView view
# using proper view and uicfg config
_pvs.tag_object_of(('*', 'sender', 'EmailAddress'), 'hidden')
_pvs.tag_object_of(('*', 'recipients', 'EmailAddress'), 'hidden')
_pvs.tag_object_of(('*', 'cc', 'EmailAddress'), 'hidden')

_afs = uicfg.autoform_section
_afs.tag_object_of(('*', 'sender', 'EmailAddress'), 'main', 'hidden')
_afs.tag_object_of(('*', 'recipients', 'EmailAddress'), 'main', 'hidden')
_afs.tag_object_of(('*', 'cc', 'EmailAddress'), 'main', 'hidden')
_afs.tag_subject_of(('*', 'generated_by', 'Email'), 'main', 'hidden')

class EmailPartIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('EmailPart')

    def parent_entity(self):
        return self.entity.email

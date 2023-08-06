from dockitresource.resources import DocumentResource, DotpathResource

from dockitcms.signals import request_reload_site, post_init_applications


class ReloadCMSSiteMixin(object):
    """
    When an item belonging to this resource is modified the CMS site gets reloaded
    """
    def on_create_success(self, item):
        request_reload_site.send(sender=self)
        return super(ReloadCMSSiteMixin, self).on_create_success(item)
    
    def on_update_success(self, item):
        request_reload_site.send(sender=self)
        return super(ReloadCMSSiteMixin, self).on_update_success(item)
    
    def on_delete_success(self, item):
        request_reload_site.send(sender=self)
        return super(ReloadCMSSiteMixin, self).on_delete_success(item)

class CMSDocumentResource(DocumentResource):
    pass

class ReloadCMSDotpathResource(ReloadCMSSiteMixin, DotpathResource):
    pass

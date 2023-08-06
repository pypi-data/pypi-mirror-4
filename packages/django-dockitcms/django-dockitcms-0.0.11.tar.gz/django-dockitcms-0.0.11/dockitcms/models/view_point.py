from __future__ import unicode_literals

from dockit import schema

from dockitcms.scope import ScopeList, Scope, get_site_scope
from dockitcms.models.mixin import create_document_mixin, ManageUrlsMixin
from dockitcms.models.collection import Collection

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse


SUBSITE_MIXINS = {}
SUBSITE_RESOURCE_MIXINS = {}
VIEW_POINT_MIXINS = {}


class Subsite(schema.Document, ManageUrlsMixin, create_document_mixin(SUBSITE_MIXINS)):
    url = schema.CharField()
    name = schema.CharField()
    slug = schema.SlugField()
    sites = schema.ModelSetField(Site, blank=True)

    def __unicode__(self):
        return '%s - %s' % (self.name, self.url)

    def get_logger(self):
        from dockitcms.sites import logger
        return logger

    @property
    def resource_definitions(self):
        return PublicResource.objects.filter(subsite=self)

    def get_site_client(self):
        """
        Returns a hyperadmin client for public consumption
        """
        from dockitcms.resources.virtual import site
        from dockitcms.resources.public import PublicSubsite

        subsite_api = PublicSubsite(api_endpoint=site, name=self.name, subsite=self)

        for resource_def in self.resource_definitions:
            try:
                resource_def.register_public_resource(subsite_api)
            except Exception as error:
                self.get_logger().exception('Could not register public resource')

        return subsite_api

    def get_urls(self):
        if not hasattr(self, '_client'):
            self._client = self.get_site_client()
        client = self._client

        return client.get_urls()

    @property
    def urls(self):
        #urls, app_name, namespace
        try:
            self.urlpatterns
        except Exception as error:
            logger = self.get_logger()
            logger.exception('Error while constructing urls')
            raise
        return self, None, self.name

    @property
    def urlpatterns(self):
        return self.get_urls()

Subsite.objects.index('sites').commit()
Subsite.objects.index('slug').commit()


class BaseViewPoint(ManageUrlsMixin, create_document_mixin(VIEW_POINT_MIXINS)):
    def send_view_point_event(self, event, view, kwargs):
        '''
        The view calls this to notify the mixins that an event has happened
        '''
        mixins = self.get_active_mixins(self)
        results = []
        for mixin_cls in mixins:
            if not hasattr(mixin_cls, 'handle_view_point_event'):
                continue
            mixin = mixin_cls(_primitive_data=self._primitive_data)
            val = mixin.handle_view_point_event(event, view, kwargs)
            results.append((mixin, val))
        return results

    def get_scopes(self):
        site_scope = get_site_scope()

        subsite_scope = Scope('subsite', object=self.subsite)
        subsite_scope.add_data('object', self.subsite, self.subsite.get_manage_urls())

        viewpoint_scope = Scope('viewpoint', object=self)
        viewpoint_scope.add_data('object', self, self.get_manage_urls())

        return ScopeList([site_scope, subsite_scope, viewpoint_scope])

    def get_view_endpoints(self):
        """
        returns a list of tuples
        [(endpoint_cls, kwargs)...]
        """
        return []

    def register_view_endpoints(self, site):
        pass

    def get_absolute_url(self):
        return self.reverse('index')

    def reverse(self, name, *args, **kwargs):
        if not name.startswith('dockitcms:%s:' % self.pk):
            name = 'dockitcms:%s:%s' % (self.pk, name)
        try:
            return reverse(name, args=args, kwargs=kwargs)#, current_app=self.subsite.name)
        except Exception as error:
            print error
            raise

    class Meta:
        typed_field = 'view_type'
        verbose_name = 'View Point'


class ViewPoint(BaseViewPoint):
    url = schema.CharField(help_text='May be a regular expression that the url has to match', blank=True)
    endpoint_name = schema.CharField(blank=True)
    url_name = schema.CharField(blank=True)

    default_endpoint_name = None

    def get_endpoint_name(self):
        return self.endpoint_name or self.default_endpoint_name

    def get_view_endpoint_kwargs(self, **kwargs):
        params = {
            'url_suffix': self.get_url(),
        }
        if self.url_name:
            params['name_suffix'] = self.url_name
        params.update(kwargs)
        return params

    def get_url(self):
        url = self.url or ''
        if url.startswith('/'):
            url = url[1:]
        if not url.startswith('^'):
            url = '^' + url
        return url

    def get_url_regexp(self):
        url = self.get_url()
        return r'%s' % url

    def __unicode__(self):
        if self.url:
            return self.url
        else:
            return self.view_type

    class Meta:
        proxy = True


class PublicResource(schema.Document, create_document_mixin(SUBSITE_RESOURCE_MIXINS)):
    subsite = schema.ReferenceField(Subsite)

    url = schema.CharField()
    name = schema.CharField()

    def get_base_url(self):
        url = self.url or ''
        if url.startswith('/'):
            url = url[1:]
        if not url.startswith('^'):
            url = '^' + url
        return url

    def get_public_resource_class(self):
        from dockitcms.resources.public import PublicResource
        return PublicResource

    def get_public_resource_kwargs(self, **kwargs):
        collection = self.collection
        params = {
            'collection': collection,
            'base_url': self.get_base_url(),
            'app_name': collection.application.slug,
            'resource_adaptor': collection.get_collection_resource().resource_adaptor,
            'view_points':[],
        }
        params.update(kwargs)
        return params

    def register_public_resource(self, site):
        klass = self.get_public_resource_class()
        kwargs = self.get_public_resource_kwargs(site=site)
        return site.register_endpoint(klass, **kwargs)

    class Meta:
        typed_field = '_resource_type'

PublicResource.objects.index('subsite').commit()


class PublicCollectionResource(PublicResource):
    collection = schema.ReferenceField(Collection)
    view_points = schema.ListField(schema.SchemaField(BaseViewPoint))

    @property
    def cms_resource(self):
        return self.collection.get_collection_resource()

    def get_public_resource_kwargs(self, **kwargs):
        kwargs.setdefault('view_points', self.view_points)
        return super(PublicCollectionResource, self).get_public_resource_kwargs(**kwargs)

    class Meta:
        typed_key = 'collection'

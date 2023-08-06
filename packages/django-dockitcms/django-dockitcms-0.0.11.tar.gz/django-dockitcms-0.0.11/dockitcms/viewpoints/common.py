from dockit import schema

from hyperadmin.clients.views import ListView, DetailView

from dockitcms.viewpoints.views import ConfigurableTemplateResponseMixin
from dockitcms.models import Collection
from dockitcms.scope import Scope

from django.utils.translation import ugettext_lazy as _
from django.template import Template, Context
from django.utils.safestring import mark_safe

#TODO lazy mark safe
LIST_CONTEXT_DESCRIPTION = _('''
Context:<br/>
<em>object_list</em> <span>The list of items</span><br/>
<em>page</em> <span>Page object if paginate by is supplied</span><br/>
<em>paginator</em> <span>Paginator object if paginate by is supplied</span><br/>
''')

DETAIL_CONTEXT_DESCRIPTION = _('''
Context:<br/>
<em>object</em> <span>The currently viewed object</span><br/>
''')


class PointListView(ConfigurableTemplateResponseMixin, ListView):
    pass

class PointDetailView(ConfigurableTemplateResponseMixin, DetailView):
    def get_scopes(self):
        scopes = super(PointDetailView, self).get_scopes()
        obj = self.get_object()
        object_scope = Scope('object', object=obj)
        if hasattr(obj, 'get_manage_urls'):
            manage_urls = obj.get_manage_urls()
        else:
            manage_urls = dict()
        object_scope.add_data('object', obj, manage_urls)
        scopes.append(object_scope)
        return scopes

TEMPLATE_SOURCE_CHOICES = [
    ('name', _('By Template Name')),
    ('html', _('By Template HTML')),
]

class TemplateMixin(schema.Schema):
    '''
    View point mixin that allows for template rendering to be overriden.
    '''
    template_source = schema.CharField(choices=TEMPLATE_SOURCE_CHOICES, default='name')
    template_name = schema.CharField(default='dockitcms/list.html', blank=True)
    template_html = schema.TextField(blank=True)
    content = schema.TextField(blank=True)
    
    def render_content(self, context):
        if self.content:
            template = Template(self.content)
            return mark_safe(template.render(Context(context)))
        return ''
    
    def get_template_names(self):
        if self.template_source == 'name':
            return [self.template_name]
        if self.template_source == 'html':
            return Template(self.template_html)

class IndexMixin(schema.Schema):
    '''
    View point mixin that allows for index selection
    '''
    index_name = schema.CharField(blank=True) #TODO populate based on available indexes to resource
    
    def get_view_endpoint_kwargs(self, **kwargs):
        params = {}
        if self.index_name:
            params['index_name'] = self.index_name
        params.update(kwargs)
        return super(IndexMixin, self).get_view_endpoint_kwargs(**params)

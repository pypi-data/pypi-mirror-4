from django.views.generic.base import TemplateResponseMixin
from django.template import Template, Context
from django.utils.safestring import mark_safe

from dockitcms.models.mixin import EventMixin, PreEventFunction, CollectEventFunction, PostEventFunction

from dockitcms.viewpoints.exceptions import HttpException

class VPViewMixin(EventMixin): #should be mixed into all view classes by view points
    view_point = None
    
    def get_scopes(self):
        return self.view_point.get_scopes()
    
    def get_active_mixins(self, target=None):
        assert getattr(self.view_point, '_mixin_bound', False)
        target=target or self.view_point
        return self.view_point.get_active_mixins(target=target)
    
    def send_mixin_event(self, event, kwargs):
        kwargs['view'] = self
        return EventMixin.send_mixin_event(self, event, kwargs)
    
    def dispatch(self, request, *args, **kwargs):
        try:
            self.send_mixin_event('dispatch', {'request':request, 
                                               'args':args, 
                                               'kwargs':kwargs,})
            return super(VPViewMixin, self).dispatch(request, *args, **kwargs)
        except HttpException, error:
            return error.response
    
    #on the return of the following functions at the top level, fire the event
    mixin_function_events = {
        'get_object': {
            'post': PostEventFunction(event='view.object', keyword='object'),
        },
        'get_context_data': {
            'post': PostEventFunction(event='view.context', keyword='context'),
        },
        'render_to_response':{
            'post': PostEventFunction(event='view.response', keyword='response'),
        },
        'get_queryset':{
            'post': PostEventFunction(event='view.queryset', keyword='queryset'),
        },
        'get_scopes':{
            'collect': CollectEventFunction(event='view.collect_scopes'),
            'post': PostEventFunction(event='view.scopes', keyword='scopes'),
        },
        'get_template_names':{
            'post': PostEventFunction(event='view.template_names', keyword='template_names'),
        },
    }

class ConfigurableTemplateResponseMixin(VPViewMixin, TemplateResponseMixin):
    """
    A mixin that can be used to render a template.
    """
    configuration = None
    
    def render_content(self, context):
        if 'content' in self.configuration:
            template = Template(self.configuration['content'])
            return mark_safe(template.render(Context(context)))
        return ''
    
    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response with a template rendered with the given context.
        """
        #TODO this should be view_point.content
        context['content'] = self.render_content(context)
        context['scopes'] = self.get_scopes()
        
        return self.response_class(
            request = self.request,
            template = self.get_template_names(),
            context = context,
            **response_kwargs
        )
    
    def get_template_names(self):
        if self.configuration['template_source'] == 'name':
            return [self.configuration['template_name']]
        if self.configuration['template_source'] == 'html':
            return Template(self.configuration['template_html'])
        assert False, str(self.configuration)


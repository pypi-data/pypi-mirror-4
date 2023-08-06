from dockit.forms import DocumentForm
from django import forms

from dockitcms.widgetblock.models import BaseTemplateWidget
from dockitcms.widgetblock.builtins import CTAWidget

class BaseTemplateWidgetForm(DocumentForm):
    class Meta:
        schema = BaseTemplateWidget

class CTAWidgetForm(BaseTemplateWidgetForm):
    template_name = forms.CharField(required=False, initial='widgetblock/cta_widget.html')
    
    class Meta:
        schema = CTAWidget

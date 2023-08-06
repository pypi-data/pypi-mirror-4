from django.forms.models import ModelChoiceField, Field
from django.forms import ChoiceField
from django.forms.fields import EMPTY_VALUES

from smart_generic.widgets import ChainedSelect, GenericChainedSelect


class GenericChainedModelChoiceField(ModelChoiceField):
    
    def __init__(self, chain_field, model_field, initial=None, *args, **kwargs):
            
            defaults = {
                        'widget': GenericChainedSelect(chain_field, model_field),
            }
            defaults.update(kwargs)
            super(GenericChainedModelChoiceField, self).__init__(initial=initial, *args, **defaults)
    
    def _get_choices(self):
        
        self.widget.queryset = self.queryset
        choices = super(GenericChainedModelChoiceField, self)._get_choices()
        return choices
    choices = property(_get_choices, ChoiceField._set_choices)
    
    def to_python(self, value):
        return value
    
    def clean(self, value):
        
        Field.clean(self, value)
        if value in EMPTY_VALUES:
            return None
        return value
   

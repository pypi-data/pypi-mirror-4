# -*- coding: utf-8 -*-

from django.forms.models import ModelForm

from smart_generic.form_fields import GenericChainedModelChoiceField


class GenericChainedObjectForm(ModelForm):

    object_id = GenericChainedModelChoiceField(queryset='',
                                               label=u'Связанный объект',
                                               required=False,
                                               chain_field='content_type',
                                               model_field='content_type')


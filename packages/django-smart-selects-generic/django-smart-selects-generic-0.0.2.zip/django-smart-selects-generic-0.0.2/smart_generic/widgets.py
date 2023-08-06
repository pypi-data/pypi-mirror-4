from django.conf import settings
from django.forms.widgets import Select
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.db.models import get_model
from django.contrib.admin.templatetags.admin_static import static

from smart_selects.widgets import ChainedSelect, USE_DJANGO_JQUERY
try:
    from smart_selects.widgets import JQUERY_URL
except ImportError:
    JQUERY_URL = None

class GenericChainedSelect(Select):

    def __init__(self, chain_field, model_field, *args, **kwargs):
        self.chain_field = chain_field
        self.model_field = model_field
        super(Select, self).__init__(*args, **kwargs)

    class Media:
        if USE_DJANGO_JQUERY:
            js = [static('admin/%s' % i) for i in
                  ('js/jquery.min.js', 'js/jquery.init.js')]
        elif JQUERY_URL:
            js = (
                JQUERY_URL,
            )

    def render(self, name, value, attrs=None, choices=()):

        if '-' in name: # generic id
            chain_field = '-'.join(attrs['id'].rsplit('-',1)[:-1] + [self.chain_field])
        else:
            chain_field = 'id_' + self.chain_field

        url = "/".join(reverse("generic_chained_filter", kwargs={'field':self.model_field,'value':"1"}).split("/")[:-2])
        js = """
        <script type="text/javascript">
        $(function(){
            var start_value = $("select#%(chainfield)s")[0].value
            if($("#%(id)s")[0].value == "" && start_value != ""){
                $.getJSON("%(url)s/"+start_value+"/", function(j){
                    var options = '';
                    options += '<option value="">---------</option>';
                    for (var i = 0; i < j.length; i++) {
                        options += '<option value="' + j[i].value + '">' + j[i].display + '</option>';
                    }
                    $("#%(id)s").html(options);
                    $('#%(id)s option[value="%(value)s"]').attr('selected', 'selected');
                })
            }
            $("select#%(chainfield)s").change(function(){
                $.getJSON("%(url)s/"+$(this).val()+"/", function(j){
                    var options = '';
                    options += '<option value="">---------</option>';
                    for (var i = 0; i < j.length; i++) {
                        options += '<option value="' + j[i].value + '">' + j[i].display + '</option>';
                    }
                    $("#%(id)s").html(options);
                    $('#%(id)s option:first').attr('selected', 'selected');
                })
            })
        })
        </script>

        """ % {'value':value,
               'chainfield':chain_field,
               'url':url,
               'id':attrs['id']}
        final_choices=[]
        for choice in self.choices:
            self.choices = [choice]
            break
        output = super(GenericChainedSelect, self).render(name, value, attrs, choices=final_choices)
        output += js
        return mark_safe(output)

class ChainedAutocompleteSelect(ChainedSelect):

    def render(self, name, value, attrs=None, choices=()):

        if '-' in name: # form field has prefix
            chain_field = '-'.join(attrs['id'].rsplit('-',1)[:-1] + [self.chain_field])
        else:
            chain_field = 'id_' + self.chain_field
        url = "/".join(reverse("chained_filter", kwargs={'app':self.app_name,'model':self.model_name,'field':self.model_field,'value':"1"}).split("/")[:-2])
        js = """
        <script type="text/javascript">
        $(function(){
            var start_value = $("input#%(chainfield)s").val()
            if($("#%(id)s")[0].vallue == "" && start_value != ""){
                $.getJSON("%(url)s/"+start_value+"/", function(j){
                    var options = '';
                    options += '<option value="">---------</option>';
                    for (var i = 0; i < j.length; i++) {
                        options += '<option value="' + j[i].value + '">' + j[i].display + '</option>';
                    }
                    $("#%(id)s").html(options);
                    $('#%(id)s option:first').attr('selected', 'selected');
                })
            }
            $("input#%(chainfield)s").change(function(){
                $.getJSON("%(url)s/"+$(this).val()+"/", function(j){
                    var options = '';
                    options += '<option value="">---------</option>';
                    for (var i = 0; i < j.length; i++) {
                        options += '<option value="' + j[i].value + '">' + j[i].display + '</option>';
                    }
                    $("#%(id)s").html(options);
                    $('#%(id)s option:first').attr('selected', 'selected');
                })
            })
        })
        </script>

        """ % {"chainfield":chain_field, "url":url, "id":attrs['id']}
        final_choices=[]
        if value:
            item = self.queryset.filter(pk=value)[0]
            pk = getattr(item, self.model_field+"_id")
            filter={self.model_field:pk}
            filtered = get_model( self.app_name, self.model_name).objects.filter(**filter)
            for choice in filtered:
                final_choices.append((choice.pk, unicode(choice)))
        for choice in self.choices:
            self.choices = [choice]
            break
        output = super(ChainedSelect, self).render(name, value, attrs, choices=final_choices)
        output += js
        return mark_safe(output)

from django.db.models import get_model
from django.http import HttpResponse
from django.utils import simplejson
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_unicode


def generic_filterchain(request, app='', model='', field='', value=''):
    o = ContentType.objects.get(pk=int(value))
    Model = get_model(o.app_label, o.model)
    results = Model.objects.all()#.filter(**keywords)
    result = []
    try:
        with_level = getattr(results[0]._meta, 'level_attr', 0)
    except IndexError:
        with_level = 0
    for item in results:
        if not with_level:
            item_label =  smart_unicode(item)
        else:
            item_label =  u'%s %s' % ('-------' * getattr(item,
                                                  item._meta.level_attr),
                           smart_unicode(item))
        result.append({'value':item.pk, 'display':item_label})
    json = simplejson.dumps(result)
    return HttpResponse(json, mimetype='application/json')

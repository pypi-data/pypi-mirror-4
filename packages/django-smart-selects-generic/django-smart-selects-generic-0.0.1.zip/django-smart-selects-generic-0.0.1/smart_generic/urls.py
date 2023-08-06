from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('smart_generic.views',
    url(r'^filter/(?P<field>[\w\-]+)/(?P<value>[\w\-]+)/$', 'generic_filterchain', name='generic_chained_filter'),
    )

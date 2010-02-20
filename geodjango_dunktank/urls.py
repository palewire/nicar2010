from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', 'unemployment.views.index', name='unemployment-index'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        'unemployment.views.month_detail', name='unemployment-month-detail'),

    (r'^admin/', include(admin.site.urls)),

)

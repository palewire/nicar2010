from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', 'unemployment.views.index', name='unemployment-index'),

    (r'^admin/', include(admin.site.urls)),

)

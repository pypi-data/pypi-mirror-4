from django.http import HttpResponse
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', lambda x: HttpResponse('')),
    url(r'^auth/', include('zeropass.urls', namespace='zeropass')),
    url(r'^admin/', include(admin.site.urls)),
)

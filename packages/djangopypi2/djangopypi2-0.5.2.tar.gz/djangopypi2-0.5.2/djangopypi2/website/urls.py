from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.static import serve as static_serve
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'', include('djangopypi2.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

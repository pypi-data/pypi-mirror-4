from django.conf.urls.defaults import patterns, include, url
from . import views

urlpatterns = patterns('',
    url(r'^manage/$', views.index, name='djangopypi2-manage'),
)

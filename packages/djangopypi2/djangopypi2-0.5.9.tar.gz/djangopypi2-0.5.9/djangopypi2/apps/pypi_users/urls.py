from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login as auth_login
from . import views

urlpatterns = patterns('',
    url(r'^users/$', views.index, name='djangopypi2-users'),
    url(r'^users/login/$', auth_login, dict(template_name='pypi_users/login.html'), name='djangopypi2-login'),
    url(r'^users/logout/$', views.logout, name='djangopypi2-logout'),
    url(r'^users/(?P<username>[\w-]+)/$', views.user_profile, name='djangopypi2-user-profile'),
)

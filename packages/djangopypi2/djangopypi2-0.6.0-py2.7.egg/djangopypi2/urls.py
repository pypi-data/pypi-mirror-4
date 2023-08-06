from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'', include('djangopypi2.apps.pypi_ui.urls')),
    url(r'', include('djangopypi2.apps.pypi_users.urls')),
    url(r'', include('djangopypi2.apps.pypi_manage.urls')),
    url(r'', include('djangopypi2.apps.pypi_packages.urls')),
    url(r'', include('djangopypi2.apps.pypi_frontend.urls')),
)

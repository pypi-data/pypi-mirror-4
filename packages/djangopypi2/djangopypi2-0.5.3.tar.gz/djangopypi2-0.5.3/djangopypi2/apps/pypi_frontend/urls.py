# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from .feeds import ReleaseFeed
from .views import root as root_views
from .views import packages as packages_views
from .views import releases as releases_views

PACKAGE = r'(?P<package>[\w\d_\.\-]+)'
VERSION = r'(?P<version>[\w\d_\.\-]+)'

urlpatterns = patterns('',
    url('^$', root_views.root, name="djangopypi2-root"),

    url('^packages/$', packages_views.index, name='djangopypi2-package-index'),
    url('^simple/$', packages_views.simple_index, name='djangopypi2-package-index-simple'),
    url('^search/$', packages_views.search,name='djangopypi2-search'),
    url('^rss/$', ReleaseFeed(), name='djangopypi2-rss'),
    
    url('^simple/' + PACKAGE + '/$', packages_views.simple_details,
        name='djangopypi2-package-simple'),
    
    url('^pypi/$', root_views.root, name='djangopypi2-release-index'),
    url('^pypi/' + PACKAGE + '/$', packages_views.details,
        name='djangopypi2-package'),
    url('^pypi/' + PACKAGE + '/rss/$', ReleaseFeed(),
        name='djangopypi2-package-rss'),
    url('^pypi/' + PACKAGE + r'/doap\.rdf$', packages_views.doap,
        name='djangopypi2-package-doap'),
    url('^pypi/' + PACKAGE + '/manage/$', packages_views.manage,
        name='djangopypi2-package-manage'),
    url('^pypi/' + PACKAGE + '/manage/versions/$', packages_views.manage_versions,
        name='djangopypi2-package-manage-versions'),
    
    url('^pypi/' + PACKAGE + '/' + VERSION + '/$',
        releases_views.details, name='djangopypi2-release'),
    url('^pypi/' + PACKAGE + '/' + VERSION + r'/doap\.rdf$',
        releases_views.doap, name='djangopypi2-release-doap'),
    url('^pypi/' + PACKAGE + '/' + VERSION + '/manage/$',
        releases_views.manage, name='djangopypi2-release-manage'),
    url('^pypi/' + PACKAGE + '/' + VERSION + '/metadata/$',
        releases_views.manage_metadata, name='djangopypi2-release-manage-metadata'),
    url('^pypi/' + PACKAGE + '/' + VERSION + '/files/$',
        releases_views.manage_files, name='djangopypi2-release-manage-files'),
    url('^pypi/' + PACKAGE + '/' + VERSION + '/files/upload/$',
        releases_views.upload_file, name='djangopypi2-release-upload-file'),
)

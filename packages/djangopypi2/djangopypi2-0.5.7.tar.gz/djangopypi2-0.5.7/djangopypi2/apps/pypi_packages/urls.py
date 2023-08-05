from django.conf.urls.defaults import patterns, include, url
from .feeds import ReleaseFeed
from . import package_views
from . import release_views

PACKAGE = r'(?P<package_name>[\w\d_\.\-]+)'
VERSION = r'(?P<version>[\w\d_\.\-]+)'

urlpatterns = patterns('',
    url(r'^search/$'  , package_views.search,name='djangopypi2-search'),
    url(r'^rss/$'     , ReleaseFeed(), name='djangopypi2-rss'),
    url(r'^packages/$', package_views.index, name='djangopypi2-packages-index'),

    url(r'^packages/' + PACKAGE + '/$'                , package_views.details, name='djangopypi2-package'),
    url(r'^packages/' + PACKAGE + '/manage/$'         , package_views.manage, name='djangopypi2-package-manage'),
    url(r'^packages/' + PACKAGE + '/manage/versions/$', package_views.manage_versions, name='djangopypi2-package-manage-versions'),

    url(r'^packages/' + PACKAGE + '/' + VERSION + '/$'             , release_views.details, name='djangopypi2-release'),
    url(r'^packages/' + PACKAGE + '/' + VERSION + '/manage/$'      , release_views.manage, name='djangopypi2-release-manage'),
    url(r'^packages/' + PACKAGE + '/' + VERSION + '/metadata/$'    , release_views.manage_metadata, name='djangopypi2-release-manage-metadata'),
    url(r'^packages/' + PACKAGE + '/' + VERSION + '/files/$'       , release_views.manage_files, name='djangopypi2-release-manage-files'),
    url(r'^packages/' + PACKAGE + '/' + VERSION + '/files/upload/$', release_views.upload_file, name='djangopypi2-release-upload-file'),
)

from django.conf.urls import patterns, include, url
from .feeds import ReleaseFeed
from . import package_views
from . import release_views

PACKAGE = r'(?P<package_name>[\w\d_\.\-]+)'
VERSION = r'(?P<version>[\w\d_\.\-]+)'

urlpatterns = patterns('',
    url(r'^search/$'  , package_views.search,name='djangopypi2-search'),
    url(r'^rss/$'     , ReleaseFeed(), name='djangopypi2-rss'),
    url(r'^packages/$', package_views.Index.as_view(), name='djangopypi2-packages-index'),

    url(r'^packages/' + PACKAGE + '/$'       , package_views.PackageDetails.as_view(), name='djangopypi2-package'),
    url(r'^packages/' + PACKAGE + '/delete/$', package_views.DeletePackage.as_view(), name='djangopypi2-package-delete'),

    url(r'^packages/' + PACKAGE + '/' + VERSION + '/$'              , release_views.ReleaseDetails.as_view(), name='djangopypi2-release'),
    url(r'^packages/' + PACKAGE + '/' + VERSION + '/delete/$'       , release_views.DeleteRelease.as_view(), name='djangopypi2-release-delete'),
    url(r'^packages/' + PACKAGE + '/' + VERSION + '/edit-details/$' , release_views.ManageRelease.as_view(), name='djangopypi2-release-edit-details'),
    url(r'^packages/' + PACKAGE + '/' + VERSION + '/edit-metadata/$', release_views.manage_metadata, name='djangopypi2-release-edit-metadata'),
    url(r'^packages/' + PACKAGE + '/' + VERSION + '/files/$'        , release_views.manage_files, name='djangopypi2-release-manage-files'),
    url(r'^packages/' + PACKAGE + '/' + VERSION + '/files/upload/$' , release_views.upload_file, name='djangopypi2-release-upload-file'),
)

from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns(
    'filemanager.views',
    url(r'^include/$', views.FileManagerView.as_view(), name='filemanager-include'),
    url(r'^old/$', views.FileManagerView.as_view(), {'template_name': 'filemanager/filemanager.html'}, name='filemanager'),

    url(r'^$', views.FileManagerBaseView.as_view(), name='filemanager-base'),
    url(r'^list/$', views.AngFileManagerListView.as_view(), name='filemanager-list'),
    url(r'^createfolder/$', views.AngFileManagerCreateView.as_view(), name='filemanager-createfolder'),
    url(r'^rename/$', views.AngFileManagerRenameView.as_view(), name='filemanager-rename'),
    url(r'^remove/$', views.AngFileManagerRemoveView.as_view(), name='filemanager-remove'),
    url(r'^upload/$', views.AngFileManagerUploadView.as_view(), name='filemanager-upload'),
    url(r'^download/$', views.AngFileManagerDownloadView.as_view(), name='filemanager-download'),

    url(r'^(?P<fs_path>.+)/$', views.FileManagerDownloadView.as_view(), name='filemanager-download'),

)

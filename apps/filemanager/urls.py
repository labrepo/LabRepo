from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns(
    'filemanager.views',
    url(r'^include/$', views.FileManagerView.as_view(), name='filemanager-include'),
    url(r'^$', views.FileManagerView.as_view(), {'template_name': 'filemanager/filemanager.html'}, name='filemanager'),
    url(r'^(?P<fs_path>.+)/$', views.FileManagerDownloadView.as_view(), name='filemanager-download'),
)

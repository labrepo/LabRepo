from django.conf.urls import patterns, url
from .views import FileManagerView, FileManagerDownloadView

urlpatterns = patterns(
    'filemanager.views',
    url(r'^include/$', FileManagerView.as_view(), name='filemanager-include'),
    url(r'^$', FileManagerView.as_view(), {'template_name': 'filemanager/filemanager.html'}, name='filemanager'),
    url(r'^(?P<fs_path>.+)/$', FileManagerDownloadView.as_view(), name='filemanager-download'),
)

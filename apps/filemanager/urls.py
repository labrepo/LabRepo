from django.conf.urls import patterns, url
from .views import FileManagerView

urlpatterns = patterns(
    'filemanager.views',
    url(r'^include/$', FileManagerView.as_view(), name='filemanager-include'),
    url(r'^$', FileManagerView.as_view(), {'template_name': 'filemanager/filemanager.html'}, name='filemanager'),
)

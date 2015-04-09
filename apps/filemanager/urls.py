from django.conf.urls import patterns, url

urlpatterns = patterns(
    'filemanager.views',
    url(r'^include/$', 'handler', name='filemanager-include'),
    url(r'^$', 'handler', {'template_name': 'filemanager/filemanager.html'}, name='filemanager'),
)

from django.conf.urls import patterns, url
from .views import TagListView, TagCreateView, TagDeleteView, TagUpdateView


urlpatterns = patterns(
    '',
    url(r'^create/$', TagCreateView.as_view(), name='create'),
    url(r'^update/(?P<pk>[\d\w]+)/$', TagUpdateView.as_view(), name='update'),
    url(r'^delete/$', TagDeleteView.as_view(), name='delete'),
    url(r'^list/$', TagListView.as_view(), name='list'),
)

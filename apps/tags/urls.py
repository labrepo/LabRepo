from django.conf.urls import patterns, url, include
from . import views


urlpatterns = patterns(
    '',
    url(r'^create/$', views.TagCreateView.as_view(), name='create'),
    url(r'^update/(?P<pk>[\d]+)/$', views.TagUpdateView.as_view(), name='update'),
    url(r'^delete/$', views.TagDeleteView.as_view(), name='delete'),
    url(r'^list/$', views.TagListView.as_view(), name='list'),

    url(r'^api/', include('tags.api.urls')),
)

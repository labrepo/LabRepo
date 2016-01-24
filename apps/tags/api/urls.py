from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^$', views.TagListView.as_view(), name='api-list'),
    url(r'^(?P<pk>[\d]+)/$', views.TagDetailView.as_view(), name='api-detail'),
)

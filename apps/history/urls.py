from django.conf.urls import patterns, include, url
from django.contrib import admin
from mongoadmin.sites import site

from history.views import HistoryListView, HistoryDetailView


admin.autodiscover()


urlpatterns = patterns('',
    url(r'^(?P<class_name>\w+)/(?P<pk>[\d\w]+)/$', HistoryListView.as_view(), name='list'),
    url(r'^(?P<pk>[\d\w]+)/$', HistoryDetailView.as_view(), name='detail'),
)

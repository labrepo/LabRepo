from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^$', views.StorageListView.as_view(), name='api-list'),
    url(r'^(?P<pk>[\d]+)/$', views.StorageDetailView.as_view(), name='api-detail'),
)

from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^(?P<instance_type>[\d\w]+)/(?P<object_id>[\d]+)/$', views.CommentListView.as_view(), name='api-list'),
    url(r'^(?P<instance_type>[\d\w]+)/(?P<object_id>[\d]+)/(?P<pk>[\d]+)/$', views.CommentDetailView.as_view(), name='api-detail'),
)

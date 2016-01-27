from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^$', views.RecentActivityListView.as_view(), name='api-all'),
    url(r'^measurements/$', views.MeasurementActivityListView.as_view(), name='api-all-measurements'),
    url(r'^comments/$', views.CommentActivityListView.as_view(), name='api-all-comments'),

    url(r'^experiment/(?P<experiment_pk>[\d]+)/$',
        views.RecentActivityListView.as_view(),
        name='api-experiment-all'),
    url(r'^experiment/(?P<experiment_pk>[\d]+)/measurements/$',
        views.MeasurementActivityListView.as_view(),
        name='api-experiment-measurement'),
    url(r'^experiment/(?P<experiment_pk>[\d]+)/comments/$',
        views.CommentActivityListView.as_view(),
        name='api-experiment-comment'),
)

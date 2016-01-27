from django.conf.urls import patterns, include, url

from .views import (DashboardView, RecentActivityView, MeasurementRecentActivityView,
                    CommentRecentActivityView)


urlpatterns = patterns(
    '',
    url(r'^$', DashboardView.as_view(), name='dashboard'),
    url(r'^experiment/all/activity/(?P<experiment_pk>[\d]+)/$',
        RecentActivityView.as_view(),
        name='experiment-all-activity'),
    url(r'^experiment/measurement/activity/(?P<experiment_pk>[\d]+)/$',
        MeasurementRecentActivityView.as_view(),
        name='experiment-measurement-activity'),
    url(r'^experiment/comment/activity/(?P<experiment_pk>[\d]+)/$',
        CommentRecentActivityView.as_view(),
        name='experiment-comment-activity'),

    url(r'^all/activity/$',
        RecentActivityView.as_view(),
        name='all-activity'),
    url(r'^measurement/activity/$',
        MeasurementRecentActivityView.as_view(),
        name='measurement-activity'),
    url(r'^comment/activity/$',
        CommentRecentActivityView.as_view(),
        name='comment-activity'),

    url(r'^api/', include('dashboard.api.urls')),
)

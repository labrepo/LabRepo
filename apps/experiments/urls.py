from django.conf.urls import patterns, url
from experiments.views import (ExperimentCreateView, ExperimentDetailView, ExperimentUpdateView, ExperimentUpdateDateView,
                               ExperimentDeleteView)


urlpatterns = patterns('',
    url(r'^create/$', ExperimentCreateView.as_view(), name='create'),
    url(r'^update/(?P<pk>[\d\w]+)/$', ExperimentUpdateView.as_view(), name='update'),
    url(r'^edit/(?P<pk>[\d\w]+)/$', ExperimentUpdateDateView.as_view(), name='update-date'),
    url(r'^delete/(?P<pk>[\d\w]+)/$', ExperimentDeleteView.as_view(), name='delete'),
    url(r'^detail/(?P<pk>[\d\w]+)/$', ExperimentDetailView.as_view(), name='detail'),
)

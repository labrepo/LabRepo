from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^(?P<pk>[\d]+)/$', views.MeasurementDetailView.as_view(), name='api-table'),
    url(r'^(?P<pk>[\d]+)/revision/(?P<revision_pk>[\d]+)/$', views.UnitRevisionView.as_view(), name='api-revision'),
)

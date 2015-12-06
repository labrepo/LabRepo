from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^(?P<pk>[\d]+)/$', views.MeasurementDetailView.as_view(), name='api-table'),
)

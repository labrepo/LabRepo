from django.conf.urls import patterns, url
from .views import (MeasurementCreateView, MeasurementDeleteView, MeasurementDetailView,
                    MeasurementTypeCreateView, MeasurementTypeDeleteView, MeasurementTypeAppendView,
                    MeasurementDeleteOneView, MeasurementHistoryRevert)


urlpatterns = patterns('',
    url(r'^measurement_type/list/$', MeasurementTypeCreateView.as_view(), name='measurement_type_list'),
    url(r'^measurement_type/create/$', MeasurementTypeCreateView.as_view(), name='measurement_type_create'),
    url(r'^measurement_type/append/$', MeasurementTypeAppendView.as_view(), name='measurement_type_append'),
    url(r'^measurement_type/delete/$', MeasurementTypeDeleteView.as_view(), name='measurement_type_delete'),

    url(r'^(?P<unit_pk>[\d\w]+)/create/$', MeasurementCreateView.as_view(), name='create'),
    url(r'^(?P<unit_pk>[\d\w]+)/delete/$', MeasurementDeleteView.as_view(), name='delete'),
    url(r'^(?P<unit_pk>[\d\w]+)/list/$', MeasurementCreateView.as_view(), name='list'),
    url(r'^(?P<unit_pk>[\d\w]+)/(?P<pk>[\d\w]+)/detail/$', MeasurementDetailView.as_view(), name='detail'),
    url(r'^(?P<unit_pk>[\d\w]+)/(?P<pk>[\d\w]+)/delete/$', MeasurementDeleteOneView.as_view(), name='delete-one'),

    url(r'^(?P<unit_pk>[\d\w]+)/revert/(?P<revision_pk>[\d\w]+)/$', MeasurementHistoryRevert.as_view(), name='measurement-revert'),

)

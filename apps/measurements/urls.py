from django.conf.urls import patterns, url, include

from . import views


urlpatterns = patterns('',
    # url(r'^measurement_type/list/$', views.MeasurementTypeCreateView.as_view(), name='measurement_type_list'),
    # url(r'^measurement_type/create/$', views.MeasurementTypeCreateView.as_view(), name='measurement_type_create'),
    # url(r'^measurement_type/append/$', views.MeasurementTypeAppendView.as_view(), name='measurement_type_append'),
    # url(r'^measurement_type/delete/$', views.MeasurementTypeDeleteView.as_view(), name='measurement_type_delete'),

    url(r'^(?P<unit_pk>[\d]+)/create/$', views.MeasurementCreateView.as_view(), name='create'),
    url(r'^(?P<unit_pk>[\d]+)/delete/$', views.MeasurementDeleteView.as_view(), name='delete'),
    url(r'^(?P<unit_pk>[\d]+)/list/$', views.MeasurementCreateView.as_view(), name='list'),
    url(r'^(?P<unit_pk>[\d]+)/(?P<pk>[\d\w]+)/detail/$', views.MeasurementDetailView.as_view(), name='detail'),
    url(r'^(?P<unit_pk>[\d]+)/(?P<pk>[\d\w]+)/delete/$', views.MeasurementDeleteOneView.as_view(), name='delete-one'),

    url(r'^(?P<unit_pk>[\d]+)/revert/(?P<revision_pk>[\d\w]+)/$', views.MeasurementHistoryRevert.as_view(), name='measurement-revert'),

    url(r'^api/', include('measurements.api.urls')),
)

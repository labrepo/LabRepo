from django.conf.urls import patterns, url, include

from . import views


urlpatterns = patterns('',
    url(r'^(?P<unit_pk>[\d]+)/create/$', views.MeasurementTemplateView.as_view(), name='list'),

    url(r'^api/', include('measurements.api.urls')),
)

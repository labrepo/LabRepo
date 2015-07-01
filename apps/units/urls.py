from django.conf.urls import patterns, url
from .views import UnitCreateView, UnitDeleteView, UnitDetailView, UnitDeleteOneView, UnitDetailJSONView


urlpatterns = patterns('',
    url(r'^create/$', UnitCreateView.as_view(), name='create'),
    url(r'^detail/(?P<pk>[\d\w]+)/$', UnitDetailView.as_view(), name='detail'),
    url(r'^delete/$', UnitDeleteView.as_view(), name='delete'),
    url(r'^delete/(?P<pk>[\d\w]+)/$', UnitDeleteOneView.as_view(), name='delete-one'),
    url(r'^list/$', UnitCreateView.as_view(), name='list'),
    url(r'^(?P<experiment_pk>[\d\w]+)/experiment_unit_list/$', UnitCreateView.as_view(), name='experiment_unit_list'),

    url(r'^detail_json/(?P<pk>[\d\w]+)/$', UnitDetailJSONView.as_view(), name='detail-json'),
)

from django.conf.urls import patterns, url
from unit_collections.views import CollectionCreateView, CollectionUpdateView, CollectionDeleteView, CollectionListView, \
    CollectionUpdateUnitView, PlotView


urlpatterns = patterns(
    '',
    url(r'^create/$', CollectionCreateView.as_view(), name='create'),
    url(r'^update/$', CollectionUpdateUnitView.as_view(), name='unit-update'),
    url(r'^list/$', CollectionListView.as_view(), name='list'),
    url(r'^delete/$', CollectionDeleteView.as_view(), name='delete'),
    url(r'^plot/(?P<pk>[\d]+)/(?P<measurement_type_pk>[\d]+)/$', PlotView.as_view(), name='plot'),
    url(r'^update/(?P<pk>[\d]+)/$', CollectionUpdateView.as_view(), name='update'),
)

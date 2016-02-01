from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^update-table/$', views.UnitTableView.as_view(), name='api-table'),
    url(r'^unit/$', views.UnitListView.as_view(), name='api-list'),
    url(r'^unit/(?P<pk>[\d]+)/$', views.UnitDetailView.as_view(), name='api-detail'),

    url(r'^unit-links/list/(?P<unit_pk>[\d]+)/$', views.UnitLinkListView.as_view(), name='api-links-list'),
    url(r'^unit-links/(?P<pk>[\d]+)/$', views.UnitLinkDetailView.as_view(), name='api-links-detail'),
    url(r'^unit-links/$', views.UnitLinkCreateView.as_view(), name='api-links-create'),

)

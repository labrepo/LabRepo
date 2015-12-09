from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^list/$', views.UnitListView.as_view(), name='api-list-table'),
    url(r'^update-table/$', views.UnitTableView.as_view(), name='api-update-table'),
    url(r'^create/$', views.UnitCreateView.as_view(), name='api-create'),
    url(r'^update/(?P<pk>[\d]+)/$', views.UnitUpdateView.as_view(), name='api-update'),

)

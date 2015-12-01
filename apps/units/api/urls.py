from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^list/$', views.UnitListView.as_view(), name='api-list-table'),
    url(r'^update/$', views.UnitUpdateView.as_view(), name='api-update-table'),
)

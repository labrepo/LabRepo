from django.conf.urls import patterns, include, url

from . import views


urlpatterns = patterns('',
    url(r'^list/$', views.UnitTableView.as_view(), name='list'),
    url(r'^(?P<experiment_pk>[\d]+)/experiment_unit_list/$', views.UnitTableView.as_view(), name='experiment_unit_list'),

    url(r'^detail/(?P<pk>[\d]+)/$', views.UnitDetailView.as_view(), name='detail'),
    url(r'^delete/(?P<pk>[\d]+)/$', views.UnitDeleteOneView.as_view(), name='delete-one'),
    url(r'^delete/$', views.UnitDeleteView.as_view(), name='delete'),

    url(r'^(?P<pk>[\d]+)/upload/$', views.UnitFileUploadView.as_view(), name='unit-upload'),
    url(r'^(?P<pk>[\d]+)/dropxbox-upload/$', views.UnitFileDropboxUploadView.as_view(), name='unit-upload-drbox'),
    url(r'^(?P<pk>[\d]+)/local-upload/$', views.UnitFileLocalUploadView.as_view(), name='unit-upload-local'),

    url(r'^detail_json/(?P<pk>[\d]+)/$', views.UnitDetailJSONView.as_view(), name='detail-json'),

    url(r'^api/', include('units.api.urls')),
)

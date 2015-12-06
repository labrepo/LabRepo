from django.conf.urls import patterns, include, url
from . import views


urlpatterns = patterns('',
    url(r'^create/$', views.UnitCreateView.as_view(), name='create'),
    url(r'^update/$', views.UnitUpdateView.as_view(), name='update'),
    url(r'^detail/(?P<pk>[\d]+)/$', views.UnitDetailView.as_view(), name='detail'),
    url(r'^delete/$', views.UnitDeleteView.as_view(), name='delete'),
    url(r'^delete/(?P<pk>[\d]+)/$', views.UnitDeleteOneView.as_view(), name='delete-one'),
    url(r'^list/$', views.UnitCreateView.as_view(), name='list'),
    url(r'^(?P<experiment_pk>[\d]+)/experiment_unit_list/$', views.UnitCreateView.as_view(), name='experiment_unit_list'),
    url(r'^(?P<pk>[\d]+)/upload/$', views.UnitFileUploadView.as_view(), name='unit-upload'),
    url(r'^(?P<pk>[\d]+)/dropxbox-upload/$', views.UnitFileDropboxUploadView.as_view(), name='unit-upload-drbox'),
    url(r'^(?P<pk>[\d]+)/local-upload/$', views.UnitFileLocalUploadView.as_view(), name='unit-upload-local'),
    url(r'^(?P<pk>[\d]+)/add-url/$', views.CreateLinkView.as_view(), name='unit-add-url'),
    url(r'^remove-url/(?P<pk>[\d]+)$', views.DeleteLinkView.as_view(), name='unit-remove-url'),

    url(r'^detail_json/(?P<pk>[\d]+)/$', views.UnitDetailJSONView.as_view(), name='detail-json'),

    url(r'^api/', include('units.api.urls')),
)

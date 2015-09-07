from django.conf.urls import patterns, url
from .views import (UnitCreateView, UnitUpdateView, UnitDeleteView, UnitDetailView, UnitDeleteOneView,
                    UnitDetailJSONView, UnitFileUploadView, UnitFileDropboxUploadView, CreateLinkView,
                    DeleteLinkView)


urlpatterns = patterns('',
    url(r'^create/$', UnitCreateView.as_view(), name='create'),
    url(r'^update/$', UnitUpdateView.as_view(), name='update'),
    url(r'^detail/(?P<pk>[\d\w]+)/$', UnitDetailView.as_view(), name='detail'),
    url(r'^delete/$', UnitDeleteView.as_view(), name='delete'),
    url(r'^delete/(?P<pk>[\d\w]+)/$', UnitDeleteOneView.as_view(), name='delete-one'),
    url(r'^list/$', UnitCreateView.as_view(), name='list'),
    url(r'^(?P<experiment_pk>[\d\w]+)/experiment_unit_list/$', UnitCreateView.as_view(), name='experiment_unit_list'),
    url(r'^(?P<pk>[\d\w]+)/upload/$', UnitFileUploadView.as_view(), name='unit-upload'),
    url(r'^(?P<pk>[\d\w]+)/dropxbox-upload/$', UnitFileDropboxUploadView.as_view(), name='unit-upload-drbox'),
    url(r'^(?P<pk>[\d\w]+)/add-url/$', CreateLinkView.as_view(), name='unit-add-url'),
    url(r'^remove-url/(?P<pk>[\d\w]+)$', DeleteLinkView.as_view(), name='unit-remove-url'),


    url(r'^detail_json/(?P<pk>[\d\w]+)/$', UnitDetailJSONView.as_view(), name='detail-json'),
)

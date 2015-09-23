from django.conf.urls import patterns, url
from labs.views import (LabCreateView, LabListView, LabUpdateView, LabDetailView, LabDeleteView, BaseLabCreateView,
                        LabStorageCreate, LabStorageUpdate, LabStorageDelete)


urlpatterns = patterns('',
    url(r'^create/lab/$', LabCreateView.as_view(), name='create'),
    url(r'^(?P<lab_pk>[\d\w]+)/detail/lab/$', LabDetailView.as_view(), name='detail'),
    url(r'^(?P<lab_pk>[\d\w]+)/update/lab/$', LabUpdateView.as_view(), name='update'),
    url(r'^(?P<lab_pk>[\d\w]+)/delete/lab/$', LabDeleteView.as_view(), name='delete'),
    url(r'^create/test/lab/$', BaseLabCreateView.as_view(), name='create_test_lab'),
    url(r'^$', LabListView.as_view(), name='list'),

    url(r'^(?P<lab_pk>[\d\w]+)/storage/create/$', LabStorageCreate.as_view(), name='storage-create'),
    url(r'^(?P<lab_pk>[\d\w]+)/storage/(?P<pk>[\d\w]+)/edit/', LabStorageUpdate.as_view(), name='storage-update'),
    url(r'^(?P<lab_pk>[\d\w]+)/storage/(?P<pk>[\d\w]+)/delete/', LabStorageDelete.as_view(), name='storage-delete'),
)

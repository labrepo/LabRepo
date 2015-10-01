from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns('',
    url(r'^create/lab/$', views.LabCreateView.as_view(), name='create'),
    url(r'^(?P<lab_pk>[\d\w]+)/detail/lab/$', views.LabDetailView.as_view(), name='detail'),
    url(r'^(?P<lab_pk>[\d\w]+)/update/lab/$', views.LabUpdateView.as_view(), name='update'),
    url(r'^(?P<lab_pk>[\d\w]+)/delete/lab/$', views.LabDeleteView.as_view(), name='delete'),
    url(r'^create/test/lab/$', views.BaseLabCreateView.as_view(), name='create_test_lab'),
    url(r'^$', views.LabListView.as_view(), name='list'),

    url(r'^(?P<lab_pk>[\d\w]+)/storage/create/$', views.LabStorageCreate.as_view(), name='storage-create'),
    url(r'^(?P<lab_pk>[\d\w]+)/storage/(?P<pk>[\d\w]+)/edit/', views.LabStorageUpdate.as_view(), name='storage-update'),
    url(r'^(?P<lab_pk>[\d\w]+)/storage/(?P<pk>[\d\w]+)/delete/', views.LabStorageDelete.as_view(), name='storage-delete'),
)

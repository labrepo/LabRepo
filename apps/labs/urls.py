from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns('',
    url(r'^create/lab/$', views.LabCreateView.as_view(), name='create'),
    url(r'^(?P<lab_pk>[\d]+)/detail/lab/$', views.LabDetailView.as_view(), name='detail'),
    url(r'^(?P<lab_pk>[\d]+)/update/lab/$', views.LabUpdateView.as_view(), name='update'),
    url(r'^(?P<lab_pk>[\d]+)/delete/lab/$', views.LabDeleteView.as_view(), name='delete'),
    url(r'^create/test/lab/$', views.BaseLabCreateView.as_view(), name='create_test_lab'),
    url(r'^$', views.LabListView.as_view(), name='list'),

    url(r'^(?P<lab_pk>[\d]+)/storage/create/$', views.LabStorageCreate.as_view(), name='storage-create'),
    url(r'^(?P<lab_pk>[\d]+)/storage/(?P<pk>[\d]+)/edit/', views.LabStorageUpdate.as_view(), name='storage-update'),
    url(r'^(?P<lab_pk>[\d]+)/storage/(?P<pk>[\d]+)/delete/', views.LabStorageDelete.as_view(), name='storage-delete'),
)

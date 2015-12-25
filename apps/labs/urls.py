from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns('',
    url(r'^create/lab/$', views.LabCreateView.as_view(), name='create'),
    url(r'^(?P<lab_pk>[\d]+)/detail/lab/$', views.LabDetailView.as_view(), name='detail'),
    url(r'^(?P<lab_pk>[\d]+)/update/lab/$', views.LabUpdateView.as_view(), name='update'),
    url(r'^(?P<lab_pk>[\d]+)/delete/lab/$', views.LabDeleteView.as_view(), name='delete'),
    url(r'^create/test/lab/$', views.BaseLabCreateView.as_view(), name='create_test_lab'),
    url(r'^$', views.LabListView.as_view(), name='list'),
)

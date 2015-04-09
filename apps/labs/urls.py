from django.conf.urls import patterns, url
from labs.views import LabCreateView, LabListView, LabUpdateView, LabDetailView, LabDeleteView, BaseLabCreateView


urlpatterns = patterns('',
    url(r'^create/lab/$', LabCreateView.as_view(), name='create'),
    url(r'^(?P<lab_pk>[\d\w]+)/detail/lab/$', LabDetailView.as_view(), name='detail'),
    url(r'^(?P<lab_pk>[\d\w]+)/update/lab/$', LabUpdateView.as_view(), name='update'),
    url(r'^(?P<lab_pk>[\d\w]+)/delete/lab/$', LabDeleteView.as_view(), name='delete'),
    url(r'^create/test/lab/$', BaseLabCreateView.as_view(), name='create_test_lab'),
    url(r'^$', LabListView.as_view(), name='list'),
)

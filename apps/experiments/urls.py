from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^create/$', views.ExperimentCreateView.as_view(), name='create'),
    url(r'^update/(?P<pk>[\d]+)/$', views.ExperimentUpdateView.as_view(), name='update'),
    url(r'^edit/(?P<pk>[\d]+)/$', views.ExperimentUpdateDateView.as_view(), name='update-date'),
    url(r'^delete/(?P<pk>[\d]+)/$', views.ExperimentDeleteView.as_view(), name='delete'),
    url(r'^detail/(?P<pk>[\d]+)/$', views.ExperimentDetailView.as_view(), name='detail'),

    url(r'^add_units/$', views.ExperimentAddUnits.as_view(), name='add-units'),

    url(r'^read/(?P<pk>[\d]+)$', views.ExperimentReadComment.as_view(), name='read-comments'),
)

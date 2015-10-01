from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns('',
    url(r'^$', views.InviteTechnician.as_view(), name='invite'),
    url(r'^update/(?P<pk>[\d\w]+)/$', views.ProfileFormView.as_view(), name='update'),
    url(r'^detail/(?P<pk>[\d\w]+)/$', views.ProfileDetailView.as_view(), name='detail'),
)


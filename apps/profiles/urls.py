from django.conf.urls import patterns, url
from profiles.views import InviteTechnician, ProfileFormView, ProfileDetailView


urlpatterns = patterns('',
    url(r'^$', InviteTechnician.as_view(), name='invite'),
    url(r'^update/(?P<pk>[\d\w]+)/$', ProfileFormView.as_view(), name='update'),
    url(r'^detail/(?P<pk>[\d\w]+)/$', ProfileDetailView.as_view(), name='detail'),
)


from django.conf.urls import patterns, url

from .views import CommentCreateView, CommentUpdateView, CommentDeleteView


urlpatterns = patterns('',
    url(r'^$', CommentCreateView.as_view(), name='comment'),
    url(r'^(?P<pk>[\d\w]+)/update/$', CommentUpdateView.as_view(), name='update'),
    url(r'^(?P<pk>[\d\w]+)/remove/$', CommentDeleteView.as_view(), name='delete'),
)

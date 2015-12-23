from django.conf.urls import patterns, url, include

from .views import CommentCreateView, CommentUpdateView, CommentDeleteView


urlpatterns = patterns('',
    url(r'^$', CommentCreateView.as_view(), name='comment'),
    url(r'^(?P<pk>[\d]+)/update/$', CommentUpdateView.as_view(), name='update'),
    url(r'^(?P<pk>[\d]+)/remove/$', CommentDeleteView.as_view(), name='delete'),

    url(r'^api/', include('comments.api.urls')),
)

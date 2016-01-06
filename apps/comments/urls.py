from django.conf.urls import patterns, url, include

from . import views


urlpatterns = patterns('',
    url(r'^$', views.CommentCreateView.as_view(), name='comment'),
    url(r'^(?P<pk>[\d]+)/update/$', views.CommentUpdateView.as_view(), name='update'),
    url(r'^(?P<pk>[\d]+)/remove/$', views.CommentDeleteView.as_view(), name='delete'),

    url(r'^api/', include('comments.api.urls')),
)

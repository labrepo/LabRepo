from django.conf.urls import patterns, url, include


urlpatterns = patterns('',
    url(r'^api/', include('comments.api.urls')),
)

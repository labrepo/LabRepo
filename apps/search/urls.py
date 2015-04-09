from django.conf.urls import patterns, url
from .views import ElasticSearchView


urlpatterns = patterns('',
    url(r'^$', ElasticSearchView.as_view(), name='all'),
)

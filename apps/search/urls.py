from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns('',
    url(r'^$', views.ElasticSearchView.as_view(), name='all'),
)

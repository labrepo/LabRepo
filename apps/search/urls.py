from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns('',
    url(r'^$', views.ElasticSimpleSearchView.as_view(), name='all'),
)

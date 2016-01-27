from django.conf.urls import patterns, url, include

from . import views


urlpatterns = patterns('',
    url(r'^$', views.LabStorageIndex.as_view(), name='index'),

    url(r'^api/', include('storages.api.urls')),
)

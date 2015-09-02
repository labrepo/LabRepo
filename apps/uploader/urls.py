# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url


from . import views

urlpatterns = patterns(
    '',
    url(r'^uploader/delete/(?P<document_name>\w+)/(?P<pk>[\d\w]+)/$',
        views.FileDeleteView.as_view(),
        name='file-delete'),

    url(r'^uploader/download/(?P<document_name>\w+)/(?P<pk>[\d\w]+)/$',
        views.DownloadFileView.as_view(),
        name='file-download'),

)

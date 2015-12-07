# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns(
    '',
    url(r'^uploader/delete/(?P<app_name>[\w\d]+)/(?P<model_name>[\w\d]+)/(?P<pk>[\d]+)/$',
        views.FileDeleteView.as_view(),
        name='file-delete'),
)

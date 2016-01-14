from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin


admin.autodiscover()

js_info_dict = {
    'packages': ('common',),
}

urlpatterns = patterns(
    '',
    url(r'^accounts/', include('common.backends.registration.urls')),
    # url(r'^(?P<lab_pk>[\d]+)/history/', include('history.urls', namespace='history')),
    url(r'^', include('labs.urls', namespace='labs')),
    url(r'^(?P<lab_pk>[\d]+)/experiments/', include('experiments.urls', namespace='experiments')),
    # url(r'^(?P<lab_pk>[\d]+)/collections/', include('unit_collections.urls', namespace='collections')),
    url(r'^(?P<lab_pk>[\d]+)/units/', include('units.urls', namespace='units')),
    url(r'^(?P<lab_pk>[\d]+)/dashboard/', include('dashboard.urls', namespace='dashboard')),
    url(r'^(?P<lab_pk>[\d]+)/comment/', include('comments.urls', namespace='comment')),
    url(r'^(?P<lab_pk>[\d]+)/tags/', include('tags.urls', namespace='tags')),
    url(r'^(?P<lab_pk>[\d]+)/measurements/', include('measurements.urls', namespace='measurements')),
    url(r'^(?P<lab_pk>[\d]+)/search/', include('search.urls', namespace='search')),
    url(r'^(?P<lab_pk>[\d]+)/file/', include('uploader.urls', namespace='upload')),
    url(r'^(?P<lab_pk>[\d]+)/storages/', include('storages.urls', namespace='storages')),
    url(r'^profiles/', include('profiles.urls', namespace='profiles')),
    url(r"^(?P<lab_pk>[\d]+)/filemanager/", include("filemanager.urls")),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/rosetta/', include('rosetta.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict, name='js_catalog'),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'common.views.handler404'
handler500 = 'common.views.handler500'
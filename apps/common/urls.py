from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

from mongoadmin.sites import site


admin.autodiscover()

js_info_dict = {
    'packages': ('common',),
}

urlpatterns = patterns(
    '',
    url(r'^accounts/', include('common.backends.registration.urls')),
    url(r'^(?P<lab_pk>[\d\w]+)/history/', include('history.urls', namespace='history')),
    url(r'^', include('labs.urls', namespace='labs')),
    url(r'^(?P<lab_pk>[\d\w]+)/experiments/', include('experiments.urls', namespace='experiments')),
    url(r'^(?P<lab_pk>[\d\w]+)/collections/', include('unit_collections.urls', namespace='collections')),
    url(r'^(?P<lab_pk>[\d\w]+)/units/', include('units.urls', namespace='units')),
    url(r'^(?P<lab_pk>[\d\w]+)/dashboard/', include('dashboard.urls', namespace='dashboard')),
    url(r'^(?P<lab_pk>[\d\w]+)/comment/', include('comments.urls', namespace='comment')),
    url(r'^(?P<lab_pk>[\d\w]+)/tags/', include('tags.urls', namespace='tags')),
    url(r'^(?P<lab_pk>[\d\w]+)/measurements/', include('measurements.urls', namespace='measurements')),
    url(r'^(?P<lab_pk>[\d\w]+)/search/', include('search.urls', namespace='search')),
    url(r'^profiles/', include('profiles.urls', namespace='profiles')),
    url(r"^(?P<lab_pk>[\d\w]+)/filemanager/", include("filemanager.urls")),
    url(r'^ckeditor/', include('ckeditor.urls')),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/rosetta/', include('rosetta.urls')),
    url(r'^admin/', include(site.urls)),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict, name='js_catalog'),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
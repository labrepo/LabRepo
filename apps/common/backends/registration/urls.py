"""
URLconf for registration and activation, using django-registration's
default backend.

If the default behavior of these views is acceptable to you, simply
use a line like this in your root URLconf to set up the default URLs
for registration::

    (r'^accounts/', include('registration.backends.default.urls')),

This will also automatically set up the views in
``django.contrib.auth`` at sensible default locations.

If you'd like to customize registration behavior, feel free to set up
your own URL patterns for these views instead.

"""


from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateView
from django.contrib.auth import views as auth_views
from common.backends.registration.forms import ResetPasswordForm, EmailAuthenticationForm, PasswordSetForm

from .views import ActivationView, RegistrationView, DemoLogin


urlpatterns = patterns('',
                       url(r'^register/$',
                           RegistrationView.as_view(),
                           name='registration_register'),
                       url(r'^register/complete/$',
                           TemplateView.as_view(template_name='registration/registration_complete.html'),
                           name='registration_complete'),
                       url(r'^register/closed/$',
                           TemplateView.as_view(template_name='registration/registration_closed.html'),
                           name='registration_disallowed'),
                       url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           auth_views.password_reset_confirm, {'set_password_form': PasswordSetForm},
                           name='password_reset_confirm_auth'),
                       url(r'^password_reset/$',
                           'django.contrib.auth.views.password_reset',
                           {'password_reset_form': ResetPasswordForm},
                           name='auth_reset_password'),

                       url(r'^activate/complete/$', 'django.contrib.auth.views.login',
                           {'template_name': 'registration/login.html', 'authentication_form': EmailAuthenticationForm, 'extra_context':{'activate':True}},
                           name='registration_activation_complete'),
                       url(r'^login/$', 'django.contrib.auth.views.login',
                           {'template_name': 'registration/login.html', 'authentication_form': EmailAuthenticationForm},
                           name='login_auth'),
                       url(r'^logout/$', 'django.contrib.auth.views.logout_then_login',
                           name='auth_logout_then_login'),

                       # url(r'^activate/complete/$',
                       #     TemplateView.as_view(template_name='registration/activation_complete.html'),
                       #     name='registration_activation_complete'),
                       # Activation keys get matched by \w+ instead of the more specific
                       # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
                       # that way it can return a sensible "invalid key" message instead of a
                       # confusing 404.
                       url(r'^activate/(?P<activation_key>\w+)/$',
                           ActivationView.as_view(),
                           name='registration_activate'),

                       (r'', include('registration.auth_urls')),
                       (r'', include('django.contrib.auth.urls')),

                       url(r'^demo_login/$', DemoLogin.as_view(), name='demo_login'),
                       )

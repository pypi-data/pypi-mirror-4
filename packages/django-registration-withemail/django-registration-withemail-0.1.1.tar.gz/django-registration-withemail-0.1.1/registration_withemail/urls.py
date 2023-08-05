"""
URLconf for registration and activation.

add this line in your root URLconf to set up the default URLs
for django-registration-email::

(r'^accounts/', include('registration_withemail.urls')),

This will also automatically set up the views in ``django.contrib.auth``.

If you'd like to customize the behavior (e.g., by passing extra
arguments to the various views) or split up the URLs, feel free to set
up your own URL patterns for these views instead.

"""

from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from registration_withemail.views import register, activate

urlpatterns = patterns('',
	url(r'^activate/complete/$', TemplateView.as_view(template_name="registration/activation_complete.html"), name='registration_activation_complete'),
		# Activation keys get matched by \w+ instead of the more specific
		# [a-fA-F0-9]{40} because a bad activation key should still get to the view;
		# that way it can return a sensible "invalid key" message instead of a confusing 404.
   	url(r'^activate/(?P<activation_key>\w+)/$', activate, name='registration_activate'),
	url(r'^register/$', register, name='registration_register'),
	url(r'^register/complete/$', TemplateView.as_view(template_name="registration/registration_complete.html"), name='registration_complete'),
	(r'', include('registration_withemail.auth_urls')),
)
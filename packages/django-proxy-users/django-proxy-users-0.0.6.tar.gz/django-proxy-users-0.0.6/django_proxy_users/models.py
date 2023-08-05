from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

if 'django_proxy_users.auth.backends.LoginAsBackend' not in settings.AUTHENTICATION_BACKENDS:
    raise ImproperlyConfigured('django_proxy_users requires the django_proxy_users.auth.backends.LoginAsBackend')

if 'django_proxy_users.auth.backends.LogBackInAsBackend' not in settings.AUTHENTICATION_BACKENDS:
    raise ImproperlyConfigured('django_proxy_users requires the django_proxy_users.auth.backends.LogBackInAsBackend')

if 'django.contrib.auth.backends.ModelBackend' not in settings.AUTHENTICATION_BACKENDS:
    raise ImproperlyConfigured('django_proxy_users requires the django.contrib.auth.backends.ModelBackend')

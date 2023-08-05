from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import models as DjangoAuthModels
from django_proxy_users import settings as ProxyUsersSettings

SESSION_ORIGINAL_USER_KEY = ProxyUsersSettings.SESSION_ORIGINAL_USER_KEY


class BaseBackend(ModelBackend):
    """
    Authenticates against django.contrib.auth.models.User.
    """

    def get_user(self, user_id):
        try:
            return DjangoAuthModels.User.objects.get(pk=user_id)
        except DjangoAuthModels.User.DoesNotExist:
            return None


class LoginAsBackend(BaseBackend):
    """
    Authenticates against django.contrib.auth.models.User.
    """

    def authenticate(self, from_user, to_user):
        if not from_user.is_superuser or to_user.is_superuser:
            return None

        return to_user


class LogBackInAsBackend(BaseBackend):
    """
    Authenticates against django.contrib.auth.models.User.
    """

    def authenticate(self, request):
        user_id = request.session.get(SESSION_ORIGINAL_USER_KEY, False)
        if user_id:
            return DjangoAuthModels.User.objects.get(pk=user_id)
        return None

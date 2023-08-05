from django.contrib.auth import models as DjangoAuthModels
from django_proxy_users import settings as ProxyUsersSettings

SESSION_ORIGINAL_USER_KEY = ProxyUsersSettings.SESSION_ORIGINAL_USER_KEY
TEMPLATE_ORIGINAL_USER_KEY = ProxyUsersSettings.TEMPLATE_ORIGINAL_USER_KEY


def login_as(request):
    data = {}
    user_id = request.session.get(SESSION_ORIGINAL_USER_KEY, False)
    if request.user.is_authenticated:
        try:
            data = {
                TEMPLATE_ORIGINAL_USER_KEY: DjangoAuthModels.User.objects.get(pk=user_id),
            }
        except DjangoAuthModels.User.DoesNotExist:
            pass
    return data

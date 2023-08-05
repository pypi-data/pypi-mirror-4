from django.contrib import auth as DjangoAuth
from django.contrib.auth import forms as DjangoAuthForms
from django.contrib.auth import models as DjangoAuthModels
from django.core.paginator import Paginator
from django import forms as DjangoForms
from django.conf import settings
from django_proxy_users import settings as ProxyUsersSettings

SESSION_ORIGINAL_USER_KEY = ProxyUsersSettings.SESSION_ORIGINAL_USER_KEY
RECORDS_PER_PAGE = ProxyUsersSettings.RECORDS_PER_PAGE


class AuthenticationForm(DjangoAuthForms.AuthenticationForm):

    @classmethod
    def logout(self, request):
        """
        Log users out

        Keyword arguments
        request -- HttpRequest Object
        """
        DjangoAuth.logout(request)

    def login(self, request):
        """
        Log users in if the credentials passed validations.

        Keyword arguments:
        request -- HttpRequest Object
        """
        if self.is_valid():
            cleaned_data = self.cleaned_data
            user = DjangoAuth.authenticate(
                username=cleaned_data.get('username'),
                password=cleaned_data.get('password')
            )
            DjangoAuth.login(request, user)


class AuthenticateAsForm(DjangoForms.Form):

    _users = DjangoAuthModels.User.objects.filter(is_superuser=False)
    _paginator = None
    _page = 1

    find_user = DjangoForms.CharField(required=False)
    user = DjangoForms.ModelChoiceField(
        queryset=_users,
        widget=DjangoForms.RadioSelect
    )

    def __init__(self, *args, **kwargs):

        if kwargs.get('page', False):
            self._page = kwargs['page']
            del kwargs['page']

        super(AuthenticateAsForm, self).__init__(*args, **kwargs)
        if kwargs.get('data', False) and kwargs.get('data').get('find_user', False):
            self._users = self._users.filter(username__contains=kwargs.get('data').get('find_user'))
        self.fields.get('user').choices = tuple([(user.pk, user.username) for user in self._users])

    @property
    def users(self):
        """
        Return a list of users that apply to
        """
        if not self._paginator:
            paginator = Paginator(self._users, RECORDS_PER_PAGE)
            try:
                self._paginator = paginator.page(self._page)
            except Paginator.PageNotAnInteger:
                # If page is not an integer, deliver first page.
                self._paginator = paginator.page(1)
            except Paginator.EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                self._paginator = paginator.page(paginator.num_pages)
        return self._paginator

    def login_as(self, request):
        """
        Log users in if the credentials passed validations.

        Keyword arguments:
        request -- HttpRequest Object
        """
        if self.is_valid():
            login_back_to_user = request.user
            cleaned_data = self.cleaned_data
            user = DjangoAuth.authenticate(from_user=request.user, to_user=cleaned_data.get('user'))
            if user:
                DjangoAuth.login(request, user)
                if 'django_proxy_users.auth.backends.LogBackInAsBackend' in settings.AUTHENTICATION_BACKENDS:
                    request.session[SESSION_ORIGINAL_USER_KEY] = login_back_to_user.pk
                return True
            else:
                return False

    @classmethod
    def log_back_in_as(cls, request):
        """
        Log users out of proxy users and into their own account.

        Keyword arguments:
        request -- HttpRequest Object
        """
        if request.session.get(SESSION_ORIGINAL_USER_KEY, False):
            user = DjangoAuth.authenticate(request=request)
            del request.session[SESSION_ORIGINAL_USER_KEY]
            DjangoAuth.login(request, user)

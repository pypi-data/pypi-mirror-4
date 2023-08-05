from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django_proxy_users import forms as ProxyUsersForms
from django.contrib import messages as DjangoMessages
from django.utils.translation import ugettext as _

LOGIN_URL = "/django/proxy/users/login/"


@login_required(login_url=LOGIN_URL)
def home(request):
    """
    Home page.

    **template**

    :template:`django_proxy_users/home.html`
    """
    return render(request, 'django_proxy_users/home.html')


def login(request):
    """
    Interface to log users in.

    **POST Arguments**

    username  String.
    password  String.

    **template**

    :template:`django_proxy_users/login.html`
    """
    POST = request.POST if request.POST else None
    login_form = ProxyUsersForms.AuthenticationForm(data=POST)
    if login_form.is_valid():
        DjangoMessages.success(request, _("Access granted, Welcome!"))
        login_form.login(request)
        return redirect('home')

    return render(request, 'django_proxy_users/login.html', {
        'login_form': login_form
    })


def logout(request):
    """
    Log users out.
    """
    DjangoMessages.success(request, _("Bye Bye"))
    ProxyUsersForms.AuthenticationForm.logout(request)
    return redirect('home')


@login_required(login_url=LOGIN_URL)
def login_as(request):
    """
    Display a list of non-superusers to login as.

    **GET Arguments**

    user  int  User id to login as.

    **POST Arguments**

    find_user  String  Find user to login as.

    **template**

    :template:`django_proxy_users/login_as.html`
    """

    POST = {}
    PAGE = request.GET.get('page', 1)

    if request.POST.get('find_user', False):
        POST.update({'find_user': request.POST.get('find_user')})

    if request.GET.get('user', False):
        POST.update({'user': request.GET.get('user')})

    POST = POST if POST else None

    login_as_form = ProxyUsersForms.AuthenticateAsForm(data=POST, page=PAGE)

    if login_as_form.is_valid():
        if login_as_form.login_as(request):
            DjangoMessages.success(request, _(u"Access granted!"))
            return redirect('home')

    return render(request, 'django_proxy_users/login_as.html', {
        'login_as_form': login_as_form
    })


@login_required(login_url=LOGIN_URL)
def log_back_in_as(request):
    """
    Log super-users back into their original session.
    """

    DjangoMessages.success(request, _(u"Welcome back!"))
    ProxyUsersForms.AuthenticateAsForm.log_back_in_as(request)
    return redirect('home')

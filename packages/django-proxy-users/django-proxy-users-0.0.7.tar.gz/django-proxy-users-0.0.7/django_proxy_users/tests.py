"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.core.urlresolvers import reverse
from django.contrib.auth import models as DjangoAuthModels
from django.test.client import Client
from django.test import TestCase
from django.conf import settings
from django_proxy_users import settings as ProxyUsersSettings
from django_proxy_users.auth import backends as ProxyUsersBackends

SESSION_ORIGINAL_USER_KEY = ProxyUsersSettings.SESSION_ORIGINAL_USER_KEY
TEMPLATE_ORIGINAL_USER_KEY = ProxyUsersSettings.TEMPLATE_ORIGINAL_USER_KEY
PASSWORD = 'letmein'


class BaseTestCase(TestCase):

    backends = ("django_proxy_users.auth.backends.LoginAsBackend",
        "django_proxy_users.auth.backends.LogBackInAsBackend",
        "django.contrib.auth.backends.ModelBackend",)

    def setUp(self):
        """
        Create a list of users for our unit tests
        """

        self.curr_auth = settings.AUTHENTICATION_BACKENDS
        settings.AUTHENTICATION_BACKENDS = self.backends

        self.super_user_1 = DjangoAuthModels.User.objects.create_superuser(
            "super_user_1",
            "super_user_1@example.com",
            PASSWORD
        )
        self.super_user_2 = DjangoAuthModels.User.objects.create_superuser(
            "super_user_2",
            "super_user_2@example.com",
            PASSWORD
        )

        self.active_user_1 = DjangoAuthModels.User.objects.create_user(
            "active_user_1",
            "active_user_1@example.com",
            PASSWORD
        )

        self.active_user_2 = DjangoAuthModels.User.objects.create_user(
            "active_user_2",
            "active_user_1@example.com",
            PASSWORD
        )

        self.inactive_user_1 = DjangoAuthModels.User.objects.create_user(
            "inactive_user_1",
            "inactive_user_1@example.com",
            PASSWORD
        )
        self.inactive_user_1.is_active = False
        self.inactive_user_1.save()

        self.inactive_user_2 = DjangoAuthModels.User.objects.create_user(
            "inactive_user_2",
            "inactive_user_2@example.com",
            PASSWORD
        )
        self.inactive_user_2.is_active = False
        self.inactive_user_2.save()

    def tearDown(self):
        settings.AUTHENTICATION_BACKENDS = self.curr_auth


class AuthenticationFormTest(BaseTestCase):

    def test_inactive_user_logs_in(self):
        """
        Tests inactive users failing to login.
        Negative Test.
        """
        client = Client()
        client.post(reverse('login'), {
            "username": "inactive_user_1",
            "password": PASSWORD
        })
        response = client.get(reverse('login'))
        self.assertFalse(
            response.context['user'].is_authenticated()
        )

    def test_active_user_logs_in(self):
        """
        Tests users logging in successfully.
        Positive Test.
        """
        client = Client()
        client.post(reverse('login'), {
            "username": "active_user_1",
            "password": PASSWORD
        })
        response = client.get(reverse('home'))
        self.assertTrue(
            response.context['user'].is_authenticated()
        )

    def test_user_logs_out(self):
        """
        Tests users logging out of the site.
        Positive Testing.
        """
        client = Client()

        # Log a user in
        client.login(
            username="active_user_1",
            password=PASSWORD
        )
        client.get(reverse('logout'))
        response = client.get(reverse('login'))
        self.assertFalse(
            response.context['user'].is_authenticated()
        )


class LoginAsBackendTest(BaseTestCase):

    def test_superuser_logs_in_as_superuser(self):
        """
        Tests superusers failing to login as exiting superusers.
        Negative test.
        """

        client = Client()
        client.login(
            username=self.super_user_1.username,
            password=PASSWORD
        )
        response = client.get(reverse('login_as'), {
            'user': self.super_user_2.pk
        })

        self.assertEqual(response.status_code, 200)

    def test_superuser_logs_in_as_non_superuser(self):
        """
        Tests superusers successfully logging in as exiting non-superusers.
        Positive test.
        """
        client = Client()
        client.login(
            username=self.super_user_1.username,
            password=PASSWORD
        )
        response = client.get(reverse('login_as'), {
            'user': self.active_user_1.pk
        })

        self.assertEqual(response.status_code, 302)

    def test_non_superuser_logs_in_as_non_superuser(self):
        """
        Tests a non superuser failing to login as another user.
        Negative test.
        """
        client = Client()

        client.login(
            username=self.active_user_1.username,
            password=PASSWORD
        )
        client.get(reverse('login_as'), {
            'user': self.active_user_2.pk
        })
        response = client.get(reverse('home'))

        self.assertEqual(
            response.context['user'].pk,
            self.active_user_1.pk
        )


class LogBackInAsBackend(BaseTestCase):

    def test_superuser_logs_back_in_to_original_account(self):
        """
        Tests superusers logging back into their original account.
        Positive Test.
        """
        client = Client()
        client.login(
            username=self.active_user_1.username,
            password=PASSWORD
        )
        client.get(reverse('login_as'), {
            'user': self.active_user_2.pk
        })
        client.get(reverse('log_back_in_as'))
        response = client.get(reverse('home'))

        self.assertEqual(
            response.context['user'].pk,
            self.active_user_1.pk
        )

    def test_non_superuser_cannot_break_into_superuser_account(self):
        """
        Tests a non-superuser cannot use the AuthenticateAsForm.log_back_in_as
        class method to break into a superuser account by using the original-user
        stored in the session.
        Negative Test.
        """
        superuser_client = Client()
        superuser_client.login(
            username=self.super_user_1.username,
            password=PASSWORD
        )
        superuser_client.get(reverse('login_as'), {
            'user': self.active_user_2.pk
        })

        non_superuser_client = Client()
        non_superuser_client.login(
            username=self.active_user_1.username,
            password=PASSWORD
        )
        non_superuser_client.get(reverse('log_back_in_as'))
        response = non_superuser_client.get(reverse('home'))

        self.assertEqual(
            response.context['user'].pk,
            self.active_user_1.pk
        )


class LoginAsContextProcessorTest(BaseTestCase):

    def test_original_user_is_available_to_proxy_user(self):
        """
        Tests the original user if is accessible to the superadmin
        who logged in as a non-superuser
        """
        superuser_client = Client()
        superuser_client.login(
            username=self.super_user_1.username,
            password=PASSWORD
        )
        superuser_client.get(reverse('login_as'), {
            'user': self.active_user_2.pk
        })
        response = superuser_client.get(reverse('home'))
        self.assertEqual(
            self.super_user_1.pk,
            response.context[TEMPLATE_ORIGINAL_USER_KEY].pk
        )


class LoginAsBackendTest(BaseTestCase):

    def test_authenticate_method(self):
        """
        Tests that the authenticate method will only return
        a user if the from_user is a superuser and the to_user is not.
        Positive Test.
        """
        backend = ProxyUsersBackends.LoginAsBackend()

        # Should return targeted user
        user = backend.authenticate(
            from_user=self.super_user_1,
            to_user=self.active_user_2
        )
        self.assertEqual(
            user.pk,
            self.active_user_2.pk
        )

        # Should return None
        user = backend.authenticate(
            from_user=self.super_user_1,
            to_user=self.super_user_2
        )
        self.assertIsNone(
            user
        )

        user = backend.authenticate(
            from_user=self.active_user_1,
            to_user=self.super_user_2
        )
        self.assertIsNone(
            user
        )

        user = backend.authenticate(
            from_user=self.active_user_1,
            to_user=self.active_user_2
        )
        self.assertIsNone(
            user
        )


class LogBackInAsBackendTest(BaseTestCase):

    def test_authenticate_method(self):
        """
        Tests that the original user is stored in the session.
        """
        backend = ProxyUsersBackends.LogBackInAsBackend()
        superuser_client = Client()
        superuser_client.login(
            username=self.super_user_1.username,
            password=PASSWORD
        )
        superuser_client.get(reverse('login_as'), {
            'user': self.active_user_2.pk
        })
        user = backend.authenticate(request=superuser_client)
        self.assertEqual(self.super_user_1.pk, user.pk)

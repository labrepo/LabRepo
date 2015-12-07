from django.core.urlresolvers import reverse
from django.utils.translation import gettext_lazy as _
from django.test import TestCase
from django.core import mail

from profiles.models import LabUser
from profiles.factories import UserFactory


class RegistrationTest(TestCase):

    def test_registraion(self):
        url = reverse('registration_register')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Sign up'))

        data = {
            'email': 'user@labrepo.org',
            'password1': 'P@$$w0rd',
            'password2': 'P@$$w0rd2'
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "The two password fields didn&#39;t match.")
        self.assertEqual(LabUser.objects.count(), 0)
        data = {
            'email': 'user@labrepo.org',
            'password1': 'P@$$w0rd',
            'password2': 'P@$$w0rd'
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "An email has been sent to your email to activate your account.")
        self.assertEqual(LabUser.objects.count(), 1)
        new_user = LabUser.objects.get(email=data['email'])
         # New user must not be active.
        self.assertFalse(new_user.is_active)

        # An activation email was sent.
        self.assertEqual(len(mail.outbox), 1)

        # same email twice
        data = {
            'email': 'user@labrepo.org',
            'password1': 'P@$$w0rd',
            'password2': 'P@$$w0rd'
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, "An email has been sent to your email to activate your account.")
        self.assertContains(resp, "This email address is already in use")
        self.assertEqual(LabUser.objects.count(), 1)


# class ActivationTest(TestCase):
#     def test_page(self):
#         url = reverse('registration_complete')
#         resp = self.client.get(url)
#         self.assertEqual(resp.status_code, 200)
#         self.assertContains(resp, _('Activation complete'))


class LoginTest(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_page(self):
        url = reverse('login_auth')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Sign in'))

    def test_action(self):
        url = reverse('login_auth')

        data = {
            'username': self.user.email,
            'password': 'qwerty'
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, _('Sign in'))
        self.assertContains(resp, _('Create empty lab'))

        #check auth strictly by email
        data = {
            'username': self.user.username,
            'password': 'qwerty'
        }
        resp = self.client.post(url, data, follow=True)
        self.assertContains(resp, _('Sign in'))

        data = {
            'username': self.user.email,
            'password': 'qwerty1'
        }
        resp = self.client.post(url, data, follow=True)
        self.assertContains(resp, _('Sign in'))


class LogoutTest(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_page(self):
        url = reverse('auth_logout_then_login')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Sign in'))


class PasswordTest(TestCase):

    def test_page(self):
        url = reverse('auth_reset_password')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Reset my password'))
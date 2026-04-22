import uuid
from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from django.urls import reverse

from users.authentication import EmailAuthBackend
from users.forms import SignupUserForm

User = get_user_model()


class UserModelTest(StaticLiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')

    def test_str_returns_username(self):
        self.assertEqual(str(self.user), 'testuser')

    def test_get_absolute_url(self):
        url = self.user.get_absolute_url()
        self.assertIn(str(self.user.pk), url)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_default_photo_url_is_set(self):
        self.assertIsNotNone(self.user.photo_url)
        resp = self.client.get(self.user.photo_url)
        self.assertEqual(resp.status_code, 200)


class EmailAuthBackendTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='StrongPass123!', email='test@example.com')
        self.backend = EmailAuthBackend()

    def test_authenticate_by_email(self):
        result = self.backend.authenticate(None, username='test@example.com',
                                           password='StrongPass123!')
        self.assertEqual(result, self.user)

    def test_authenticate_wrong_password(self):
        result = self.backend.authenticate(None, username='test@example.com',
                                           password='wrongpassword')
        self.assertIsNone(result)

    def test_authenticate_wrong_email(self):
        result = self.backend.authenticate(None, username='nobody@example.com',
                                           password='StrongPass123!')
        self.assertIsNone(result)

    def test_get_user_returns_user(self):
        result = self.backend.get_user(self.user.pk)
        self.assertEqual(result, self.user)

    def test_get_user_nonexistent_returns_none(self):
        result = self.backend.get_user(uuid.uuid4())
        self.assertIsNone(result)


class SignupUserFormTest(TestCase):
    def test_valid_data_passes(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'captcha_0': 'test',
            'captcha_1': 'PASSED',
        }
        form = SignupUserForm(data=data)
        self.assertTrue(form.is_valid())

    def test_duplicate_email_is_invalid(self):
        data = {
            'username': 'newuser',
            'email': 'taken@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'captcha_0': 'test',
            'captcha_1': 'PASSED',
        }
        User.objects.create_user(username='testuser', email='taken@example.com')
        form = SignupUserForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_invalid_captcha_not_passes(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'captcha_0': 'test',
            'captcha_1': 'test',
        }
        form = SignupUserForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('captcha', form.errors)


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='StrongPass123!', email='test@example.com')

    def test_login_page_returns_200(self):
        resp = self.client.get(reverse('users:login'))
        self.assertEqual(resp.status_code, 200)

    def test_login_with_correct_credentials(self):
        resp = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'StrongPass123!',
        })
        self.assertRedirects(resp, reverse('users:profile'), 302, fetch_redirect_response=False)

    def test_login_with_email(self):
        resp = self.client.post(reverse('users:login'), {
            'username': 'test@example.com',
            'password': 'StrongPass123!',
        })
        self.assertRedirects(resp, reverse('users:profile'), 302, fetch_redirect_response=False)

    def test_login_with_wrong_password_stays_on_page(self):
        resp = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(resp.status_code, 200)


class SignupViewTest(TestCase):
    def test_signup_page_returns_200(self):
        response = self.client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, 200)

    def test_signup_with_valid_data(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'captcha_0': 'test',
            'captcha_1': 'PASSED',
        }
        resp = self.client.post(reverse('users:signup'), data)
        self.assertRedirects(resp, reverse('users:confirm_email'), 302, fetch_redirect_response=False)
        user = User.objects.filter(username='newuser', email='newuser@example.com').first()
        self.assertIsNotNone(user)
        self.assertFalse(user.is_active)

    def test_signup_with_taken_email(self):
        User.objects.create_user(username='testuser', email='taken@example.com')
        data = {
            'username': 'newuser',
            'email': 'taken@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'captcha_0': 'test',
            'captcha_1': 'PASSED',
        }
        resp = self.client.post(reverse('users:signup'), data)
        self.assertEqual(resp.status_code, 200)
        user = User.objects.filter(username='newuser').first()
        self.assertIsNone(user)

    def test_signup_with_taken_username(self):
        User.objects.create_user(username='takenuser')
        data = {
            'username': 'takenuser',
            'email': 'newuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'captcha_0': 'test',
            'captcha_1': 'PASSED',
        }
        resp = self.client.post(reverse('users:signup'), data)
        self.assertEqual(resp.status_code, 200)
        user = User.objects.filter(email='newuser@example.com').first()
        self.assertIsNone(user)

    def test_signup_with_invalid_captcha(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'captcha_0': 'test',
            'captcha_1': 'test',
        }
        resp = self.client.post(reverse('users:signup'), data)
        self.assertEqual(resp.status_code, 200)
        user = User.objects.filter(username='newuser', email='newuser@example.com').first()
        self.assertIsNone(user)


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='StrongPass123!')

    def test_profile_redirects_anonymous(self):
        resp = self.client.get(reverse('users:profile'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(urlparse(resp['Location']).path, reverse('users:login'))

    def test_profile_redirects_to_user_detail(self):
        self.client.login(username='testuser', password='StrongPass123!')
        resp = self.client.get(reverse('users:profile'))
        self.assertRedirects(resp, self.user.get_absolute_url(), 302)


class DeleteProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='StrongPass123!')

    def test_user_can_delete_own_account(self):
        self.client.login(username='testuser', password='StrongPass123!')
        resp = self.client.post(reverse('users:delete_profile'))
        self.assertRedirects(resp, reverse('index'), 302)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_anonymous_cannot_delete(self):
        resp = self.client.post(reverse('users:delete_profile'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(urlparse(resp['Location']).path, reverse('users:login'))
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())


class ResetAvatarProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='StrongPass123!', photo_url='testurl')

    def test_user_can_reset_own_avatar(self):
        self.client.login(username='testuser', password='StrongPass123!')
        resp = self.client.post(reverse('users:reset_avatar_profile'))
        self.assertRedirects(resp, reverse('users:profile'), 302, fetch_redirect_response=False)
        self.assertEqual(
            User.objects.get(pk=self.user.pk).photo_url,
            User._meta.get_field('photo_url').get_default()
        )

    def test_anonymous_cannot_reset(self):
        resp = self.client.post(reverse('users:reset_avatar_profile'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(urlparse(resp['Location']).path, reverse('users:login'))
        self.assertEqual(
            User.objects.get(pk=self.user.pk).photo_url,
            'testurl'
        )

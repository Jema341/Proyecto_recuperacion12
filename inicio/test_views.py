from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class ProtectedViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_inicio_redirects_to_login_when_not_authenticated(self):
        response = self.client.get(reverse('inicio'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_reportes_redirects_to_login_when_not_authenticated(self):
        response = self.client.get(reverse('reportes'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_inicio_returns_200_for_authenticated_user(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('inicio'))
        self.assertEqual(response.status_code, 200)

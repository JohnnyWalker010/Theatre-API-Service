from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user_data = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "test_password",
        }
        self.user = get_user_model().objects.create_user(**self.user_data)

    def test_user_login(self):
        url = reverse("user:login")
        data = {"username": "test_user", "password": "test_password"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)


class RegistrationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.token = str(RefreshToken.for_user(self.user).access_token)

    def test_user_registration(self):
        url = reverse("user:create")
        data = {
            "username": "new_user",
            "email": "new_user@example.com",
            "password": "new_password",
        }
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.post(url, data, format="json", headers=headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ProfileManagementTests(APITestCase):
    def setUp(self):
        self.user_data = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "test_password",
            "is_staff": True,
        }
        self.user = get_user_model().objects.create_user(**self.user_data)
        self.client.force_authenticate(user=self.user)

    def test_get_user_profile(self):
        url = reverse("user:manage")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user_data["username"])

    def test_update_user_profile(self):
        url = reverse("user:manage")
        updated_data = {"username": "updated_username"}
        response = self.client.patch(url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], updated_data["username"])

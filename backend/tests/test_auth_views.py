from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from backend.models import User


User = get_user_model()

class AuthAPIViewTestCase(TestCase):
    """Тестирование API-вьюхи аутентификации."""
    def setUp(self):
        """Настройка тестового клиента и пользователя."""
        self.client = APIClient()
        

    def test_user_registration(self):
        """Тест: регистрация пользователя (ожидаем 201)."""
        url = reverse("user_registration_api_v1")
        data = {
            "first_name": "Тест",
            "last_name": "Тестовский",
            "email": "test5@example.com",
            "password": "testpass123",
            "user_type": "testpass123"
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="test4@example.com").exists())


    def test_user_login(self):
        """Тест: вход пользователя (ожидаем 200)."""
        # Сначала зарегистрируем пользователя
        register_url = reverse("user_registration_api_v1")
        register_data = {
            "first_name": "Тест",
            "last_name": "Тестовский",
            "email": "test5@example.com",
            "password": "testpass123",
            "user_type": "testpass123"
        }
        self.client.post(register_url, register_data, format="json")

        # Теперь попробуем войти
        login_url = reverse("token_obtain_pair_api_v1")
        login_data = {
            "email": "test5@example.com",
            "password": "testpass123"
        }
        response = self.client.post(login_url, login_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access" in response.data)
        self.assertIn("refresh" in response.data)
        


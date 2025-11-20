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
            "last_name": "Тестов",
            "email": "test4@example.com",
            "password": "zxcvbnm,",
            "user_type": "zxcvbnm,"
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="test4@example.com").exists())






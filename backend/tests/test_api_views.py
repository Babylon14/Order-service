from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from backend.models import Shop
from unittest.mock import patch


User = get_user_model()

class ImportApiViewTestCase(TestCase):
    """Тестирование импорта данных из API"""
    def setUp(self):
        """Настройка тестового клиента и пользователя."""
        self.client = APIClient()
        # Создаём тестового пользователя
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="testpassword123"
        )
        self.client.force_authenticate(user=self.user)
        # Создаём тестовый магазин
        self.shop = Shop.objects.create(
            name="Test Shop",
            source_file="data/test_shop1.yaml",
            state=True,
            user=self.user
        )
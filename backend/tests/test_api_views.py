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
            source_file="data/test_shop.yaml",
            state=True,
            user=self.user
        )
    
    def test_start_import_all_shops_unauthorized(self):
        """Тест: запуск импорта БЕЗ аутентификации (ожидаем 401/403)."""
        url = reverse("start_import_all_shops_api_v1")
        response = self.client.post(url)
        # Предполагаем, что permission_classes = [permissions.IsAuthenticated]
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    @patch("backend.api.v1.api_views.import_all_shops_data_task")
    def test_start_import_all_shops_authorized(self, mock_task):
        """Тест: запуск импорта с аутентификацией (ожидаем 202)."""
        mock_task.delay.return_value.id = "test_task_id_12345" # Имитируем id задачи

        self.client.force_authenticate(user=self.user)
        url = reverse("start_import_all_shops_api_v1")
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data["task_id"], "test_task_id_12345")
        
        # Проверяем, что задача была вызвана
        mock_task.delay.assert_called_once()



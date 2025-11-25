from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch

from backend.models import Shop


User = get_user_model()

class ImportApiViewTestCase(APITestCase):
    """Тестирование импорта данных из API"""
    def setUp(self):
        """Общие настройки тестового клиента и пользователя."""
        # Создаём тестового пользователя
        self.import_user = User.objects.create_user(
            username="importuser@example.com",
            email="importuser@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.import_user) # Аутентификация пользователя

        # Подготовка URL-адресов для импорта и статуса
        self.start_import_all_url = reverse("start_import_all_shops_api_v1") # POST /api/v1/start-import-all-shops/
        self.start_import_shop_url = lambda shop_id: reverse("start_import_shop_api_v1", kwargs={"shop_id": shop_id}) # POST POST /api/v1/start-import-shop/<shop_id>/
        self.get_status_url = lambda task_id: reverse("get_import_status_api_v1", kwargs={"task_id": task_id}) # GET /api/v1/import-status/<task_id>/

        # Создаём тестовый магазин
        self.shop = Shop.objects.create(
            name="Test Shop for Import",
            source_file="data/test_shop.yaml",
            state=True,
            user=self.import_user
        )


    @patch("backend.api.v1.api_views.import_all_shops_data_task")
    def test_start_import_all_shops_authorized_success(self, mock_task):
        """
        Тест: запуск импорта ВСЕХ магазинов,
        (аутентифицирован, задача запускается) (ожидаем 202).
        """
        # Настройка мок: при вызове delay() вернуть объект с id
        mock_task.delay.return_value.id = "test_task_id_12345" # Имитация id задачи

        # Отправляем POST-запрос для запуска импорта
        response = self.client.post(self.start_import_all_url)

        # 1. Проверка, что статус ответа 202
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        # 2. Проверка, что ответе корректные данные
        self.assertEqual(response.data["task_id"], "test_task_id_12345")
        self.assertEqual(response.data["message"], "Импорт всех магазинов начат.")

        # 3. Проверка, что Celery-задача была вызвана (delay) один раз
        mock_task.delay.assert_called_once()


    def test_start_import_all_shops_unauthorized(self):
        """
        Тест: запуск импорта ВСЕХ магазинов (НЕ аутентифицирован),
        (ожидаем 401/403).
        """
        # Сброс аутентификации
        self.client.force_authenticate(user=None)
        
        # Отправляем POST-запрос для запуска импорта
        response = self.client.post(self.start_import_all_url)

        # 1. Проверка, что статус ответа 401 Unauthorized (или 403, в зависимости от permission_classes)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    @patch("backend.api.v1.api_views.import_shop_data_task")
    def test_start_import_shop_authorized_success(self, mock_task):
        """
        Тест: запуск импорта КОНКРЕТНОГО магазина (аутентифицирован, ожидаем 202).
        """
        mock_task.delay.return_value.id = "test_task_id_shop_67890" # Имитируем id задачи

        # Используем URL для конкретного магазина
        url = self.start_import_shop_url(self.shop.id)

        # Отпраавляем POST-запрос для запуска импорта
        response = self.client.post(url)

        # 1. Проверка, что статус ответа 202
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        # 2. Проверка, что ответе корректные данные
        self.assertEqual(response.data["task_id"], "test_task_id_shop_67890")
        self.assertEqual(response.data["message"], f"Импорт магазина {self.shop.name} начат.")

        # 3. Проверка, что задача вызвана с правильным ID магазина
        mock_task.delay.assert_called_once_with(self.shop.id, None)


    def test_get_import_status_unauthorized(self):
        """Тест: получение статуса задачи (НЕ аутентифицирован, ожидаем 401)."""
        self.client.force_authenticate(user=None)

        url = self.get_status_url("глупый_task_id")
        # Отправляем GET-запрос на эндпоинт статуса
        response = self.client.get(url)

        # 1. Проверка, что статус ответа 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


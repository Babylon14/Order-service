from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, override_settings
from rest_framework import status


User = get_user_model()

# Изолируем кэш
TEST_CACHE_TIMEOUT = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-throttle-cache"
    }
}

@override_settings(CACHES=TEST_CACHE_TIMEOUT)  # Изолируем кэш
class ThrottlingAPIViewTestCase(APITestCase):
    """Тестирование APIView с ограничением на количество запросов."""
    def setUp(self):
        """Общие настройки тестового клиента и пользователя."""
        from django.core.cache import cache
        cache.clear()

        # Создаём тестового пользователя
        self.throttle_user = User.objects.create_user(
            username="throttleuser@example.com",
            email="throttleuser@example.com",
            password="testpass123",
        )
        # Формируем URL для login (POST) входа
        self.login_url = reverse("token_obtain_pair_api_v1")
    

    def test_anon_user_global_throttling(self):
        """Тест: троттлинг для АНОНИМНОГО пользователя."""
        invalid_login_data = {
            "email": "nonexistent@example.com",
            "password": "invalid_pass"
        }

        num_requests = 11 # Пробую 11 запросов (лимит 10/min)
        response_list = []

        for i in range(num_requests):
            # Отправляем POST запрос на эндпоинт входа
            response = self.client.post(self.login_url, data=invalid_login_data, format="json")
            response_list.append(response.status_code) # Сохраняем коды ответов в список
            print(f"Запрос анонимного пользователя #{i + 1} - статус: {response.status_code}") # Отладка

        # 1. Проверка, что 11-й запрос превысит лимит (429)
        self.assertEqual( 
            response_list[10], # Ожидаем статус 429 (11-й запрос, перебор)
            status.HTTP_429_TOO_MANY_REQUESTS,
            f"Ожидался статус 429 для 11-го запроса, получен {response_list[10]}. "
            f"Ответы: {response_list}"
        )
        # 2. Проверка, что первые 10 запросов *НЕ* 429
        for i in range(10): # Индексы с 0 по 9
            self.assertNotEqual(
                response_list[i],
                status.HTTP_429_TOO_MANY_REQUESTS,
                f"Ожидался статус НЕ 429 для {i+1}-го запроса, получен {response_list[i]}. "
                f"Ответы: {response_list}"
        )

    def test_authenticated_user_global_throttling(self):
        """Тест: троттлинг для АУТЕНТИФИЦИРОВАННОГО пользователя"""
        self.client.force_authenticate(user=self.throttle_user) # Аутентификация пользователя

        # Формируем URL для получения списка контактов (требует аутентификацию)
        contact_list_url = reverse("contact_list_api_v1")

        num_requests = 101 # Пробую 101 запрос (лимит 100/min)
        response_list = []
        for i in range(num_requests):
            response = self.client.get(contact_list_url) # Отправляем GET-запрос на эндпоинт списка контактов
            response_list.append(response.status_code)
            print(f"Запрос аутентифицированного пользователя #{i + 1} - статус: {response.status_code}") # Отладка

        # 1. Проверка, что 101-й запрос превысит лимит (429)
        self.assertEqual( 
            response_list[100], # Ожидаем статус 429 (101-й запрос, перебор)
            status.HTTP_429_TOO_MANY_REQUESTS,
            f"Ожидался статус 429 для 101-го запроса, но получен {response_list[100]}. "
            f"Ответы: {response_list}"
        )
        # 2. Проверка, что первые 100 запросов *НЕ* 429
        for i in range(100): # Индексы с 0 по 99
            self.assertNotEqual(
                response_list[i],
                status.HTTP_429_TOO_MANY_REQUESTS,
                f"Ожидался статус НЕ 429 для {i+1}-го запроса, получен {response_list[i]}. "
                f"Ответы: {response_list}"
        )
            

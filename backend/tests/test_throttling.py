from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APITestCase, override_settings
from rest_framework import status


User = get_user_model()

# Изолируем кэш
TEST_CACHE_TIMEOUT = {
    "DEFAULT": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-throttle-cache"
    }
}

class ThrottlingAPIViewTestCase(APITestCase):
    """Тестирование APIView с ограничением на количество запросов."""
    def setUp(self):
        """Общие настройки тестового клиента и пользователя."""
        cache.clear()
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
                f"Ожидался статус 429 для 11-го запроса, но получен {response_list[10]}.",
                f"Ответы: {response_list}"
            )
            # 2. Проверка, что первые 10 запросов *НЕ* 429
            for i in range(10): # Индексы с 0 по 9
                self.assertNotEqual(
                    response_list[i],
                    status.HTTP_429_TOO_MANY_REQUESTS,
                    f"Ожидался статус НЕ 429 для {i+1}-го запроса, но получен {response_list[i]}. ",
                    f"Ответы: {response_list}"
            )

                

        

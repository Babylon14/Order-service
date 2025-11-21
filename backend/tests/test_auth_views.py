from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()

class AuthAPIViewTestCase(APITestCase):
    """Тестирование API-вьюхи аутентификации."""
    def setUp(self):
        """Общаие настройки тестового клиента и пользователя."""
        self.register_url = reverse("user_registration_api_v1")
        self.login_url = reverse("token_obtain_pair_api_v1")


    def test_user_registration(self):
        """Тест: регистрация пользователя (ожидаем 201).""" 
        # Данные для регистрации
        register_data = {
            "first_name": "Тест1-имя",
            "last_name": "Тест1-фамилия",
            "email": "testemail@example.com",
            "password": "test_password123",
            "password_confirm": "test_password123"
        }
        # Отправляем POST запрос с данными для регистрации
        response = self.client.post(self.register_url, register_data, format="json")

        # 1. Проверяем статус ответа (201 Created)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 2. Проверяем, что пользователь успешно зарегистрирован
        self.assertTrue(User.objects.filter(email="testemail@example.com").exists())


    def test_user_login_success(self):
        """Тест: УСПЕШНЫЙ вход пользователя (ожидаем 200)."""
        # Сначала зарегистрируем пользователя
        self.test_user_registration()

        # Данные для входа
        login_data = {
            "email": "testemail@example.com", # True
            "password": "test_password123"    # True
        }
        # Отправляем POST запрос с данными для входа
        response = self.client.post(self.login_url, login_data, format="json")

        # 1. Проверяем, что статус 200 (успешная аутентификация)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2. Проверяем, что в ответе есть токены (access и refresh)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        # 3. Проверяем, что пользователь активен
        created_user = User.objects.get(email="testemail@example.com")
        self.assertTrue(created_user.is_active)


    def test_user_login_failure_wrong_password(self):
        """Тест: вход с НЕПРАВИЛЬНЫМ паролем (ожидаем 401)."""
        # Сначала зарегистрируем пользователя
        self.test_user_registration()

        # Данные для входа с неправильным паролем
        login_data = {
            "email": "testemail@example.com", # True
            "password": "wrong_password"      # False
        }
        # Отправляем POST запрос с данными для входа
        response = self.client.post(self.login_url, login_data, format="json")

        # 1. Проверяем, что статус 401 (неправильный пароль)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # 2. Проверяем, что в ответе НЕТ токенов
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)
        # 3. Проверяем, что пользователь не активен
        created_user = User.objects.get(email="testemail@example.com")
        self.assertFalse(created_user.is_active)


    def test_user_login_failure_wrong_email(self):
        """Тест: вход с неправильным email (ожидаем 401)."""
        # Данные для входа с неправильным email
        login_data = {
            "email": "wrong_email",         # False
            "password": "test_password123"  # True
        }
        # Отправляем POST запрос на эндпоинт входа
        response = self.client.post(self.login_url, login_data, format="json")

        # 1. Проверяем, что статус 401 (неправильный email)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # 2. Проверяем, что в ответе НЕТ токенов
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)
        # 3. Проверяем, что пользователь не активен
        created_user = User.objects.get(email="testemail@example.com")
        self.assertFalse(created_user.is_active)
        


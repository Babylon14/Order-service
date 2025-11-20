from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from backend.models import Contact


User = get_user_model()

class ContactAPIViewTestCase(TestCase):
    """Тестирование API контактов."""
    def SetUp(self):
        """Настройка тестового клиента и пользователя."""
        self.client = APIClient()
        # Создаём тестового пользователя
        self.user = User.objects.create_user(
            username="contactuser@example.com",
            email="contactuser@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_contact(self):
        """Тест: создание контакта (ожидаем 201)."""
        url = reverse("contact_list_api_v1")
        data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "middle_name": "Иванович",
            "email": "ivanov@example.com",
            "phone": "+79991234567",
            "city": "Москва",
            "street": "Тестовая улица",
            "house_number": "1",
            "building": "A",
            "structure": "",
            "apartment": "10"
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Contact.objects.filter(user=self.user, email="ivanov@example.com").exists())


    def test_get_contacts_list(self):
        """Тест: получение списка контактов."""
        Contact.objects.create(
            user=self.user,
            first_name="Тест",
            last_name="Контакт",
            email="test_contact@example.com",
            phone="+70000000000",
            city="Тест",
            street="Тест",
            house_number="1"
        )
        url = reverse("contact_list_api_v1")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)



from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from backend.models import Contact


User = get_user_model()

class ContactAPIViewTestCase(APITestCase):
    """Тестирование API контактов."""
    def setUp(self):
        """Общие настройки тестового клиента и пользователя."""
        # Создаём тестового пользователя
        self.contact_user = User.objects.create_user(
            username="contactuser@example.com",
            email="contactuser@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.contact_user) # Аутентификация пользователя

        # Создание тестового контакта для CRUD тестов
        self.contact_data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "email": "testivanov@example.com",
            "phone": "+79999999999",
            "city": "Москва",
            "street": "Тестовая улица",
            "house": "1",
            "building": "A",
            "structure": "",
            "apartment": "1111"
        }
        self.contact = Contact.objects.create(user=self.contact_user, **self.contact_data)

        # Url-адреса для тестирования
        self.contact_list_url = reverse("contact_list_api_v1") # GET /api/v1/contacts/, POST /api/v1/contacts/


    def test_create_contact(self):
        """Тест: POST-создание контакта."""
        new_contact_data = {
            "first_name": "Петр",
            "last_name": "Петров",
            "email": "petrov@example.com",
            "phone": "+79997654321",
            "city": "Санкт-Петербург",
            "street": "Невский проспект",
            "house": "2",
            "building": "",
            "structure": "Б",
            "apartment": "20"
        }
        # Отправляем POST-запрос на эндпоинт создания контакта
        response = self.client.post(self.contact_list_url, new_contact_data, format="json")

        # 1. Проверка на успешное создание контакта (201 Created)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 2. Проверка, что данные корретны
        self.assertEqual(response.data["first_name"], "Петр")
        self.assertEqual(response.data["last_name"], "Петров")
        self.assertEqual(response.data["email"], "petrov@example.com")
        # 3. Проверка, что контакт был создан в БД
        self.assertTrue(Contact.objects.filter(user=self.contact_user, email="petrov@example.com").exists())


    def test_get_contacts_list(self):
        """Тест: GET-получение списка контактов."""
        # 1. Проверка, что контакт, созданный в setUp, существует
        self.assertTrue(Contact.objects.filter(user=self.contact_user).count(), 1)

        # Отправляем GET-запрос на эндпоинт списка контактов
        response = self.client.get(self.contact_list_url)

        # 2. Проверка на успешное получение списка контактов (200 OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 3. Проверка, что в списке один контакт
        self.assertEqual(len(response.data), 1)
        # 4. Проверка, что данные контакта совпадают
        self.assertEqual(response.data[0]["first_name"], self.contact_data["first_name"])
        self.assertEqual(response.data[0]["email"], self.contact_data["email"])
    

    def test_get_contact_detail(self):
        """Тест: GET-получение конкретного контакта."""
        contact_detail_url = reverse("contact_detail_api_v1", kwargs={"id": self.contact.id}) 
        # GET /api/v1/contacts/<int:contact_id>/,
        # PUT /api/v1/contacts/<int:contact_id>/, PATCH /api/v1/contacts/<int:contact_id>/, 
        # DELETE /api/v1/contacts/<int:contact_id>/

        # Отправляем GET-запрос на эндпоинт детализации контакта
        response = self.client.get(contact_detail_url)

        # 1. Проверка на успешное получение контакта (200 OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2. Проверка, что данные контакта совпадают
        self.assertEqual(response.data["id"], self.contact.id)
        self.assertEqual(response.data["first_name"], self.contact_data["first_name"])
        self.assertEqual(response.data["email"], self.contact_data["email"])
    

    def test_update_contact(self):
        """Тест: PUT-обновление данных контакта."""
        updated_data = {
            "first_name": "Сидор",
            "last_name": "Сидоров",
            "email": "sidorov@example.com",
            "phone": "+79991112233",
            "city": "Новосибирск",
            "street": "Красный проспект",
            "house": "3",
            "building": "В",
            "structure": "",
            "apartment": "30"
        }
        contact_detail_url = reverse("contact_detail_api_v1", kwargs={"id": self.contact.id}) 
        # Отправляем PUT-запрос на эндпоинт обновления контакта
        response = self.client.put(contact_detail_url, updated_data, format="json")

        # 1. Проверка на успешное обновление контакта (200 OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2. Проверка, что данные в ответе обновились
        self.assertEqual(response.data["first_name"], "Сидор")
        self.assertEqual(response.data["email"], "sidorov@example.com")
        # 3. Проверка, что данные обновились в БД
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.first_name, "Сидор")
        self.assertEqual(self.contact.email, "sidorov@example.com")


    def test_partial_update_contact(self):
        """Тест: PATCH-частичное обновление данных контакта."""
        partial_data = {
            "first_name": "Трофим",  # Обновляем имя
            "phone": "+79995556677", # Обновляем телефон
        }
        contact_detail_url = reverse("contact_detail_api_v1", kwargs={"id": self.contact.id}) 
        # Отправляем PATCH-запрос на эндпоинт обновления контакта
        response = self.client.patch(contact_detail_url, partial_data, format="json")

        # 1. Проверка на успешное обновление контакта (200 OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2. Проверка, что имя  и телефон обновлены
        self.assertEqual(response.data["first_name"], "Трофим")
        self.assertEqual(response.data["phone"], "+79995556677")
        # 3. Проверка, что другие поля остались прежними (например, last_name)
        self.assertEqual(response.data["last_name"], self.contact_data["last_name"])
        # 4. Проверка, что данные обновились в БД
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.first_name, "Трофим")
        self.assertEqual(self.contact.phone, "+79995556677")
        self.assertEqual(self.contact.last_name, self.contact_data["last_name"])
    

    def test_delete_contact(self):
        """Тест: DELETE-удаление контакта."""
        # 1. Проверка, что контакт существует 
        self.assertTrue(Contact.objects.filter(id=self.contact.id).exists())

        contact_detail_url = reverse("contact_detail_api_v1", kwargs={"id": self.contact.id}) 
        # Отправляем DELETE-запрос на эндпоинт удаления контакта
        response = self.client.delete(contact_detail_url)

        # 2. Проверка на успешное удаление контакта (204 No Content)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # 3. Проверка, что контакт удален из БД
        self.assertFalse(Contact.objects.filter(id=self.contact.id).exists())
        
        
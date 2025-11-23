from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from backend.models import (Order, OrderItem, Cart, CartItem, ProductInfo,
                             Shop, Product, Category, Contact)


User = get_user_model()

class OrderAPIViewTestCase(APITestCase):
    """Тестирование API заказов."""
    def setUp(self):
        """Общие настройки тестового клиента и пользователя."""
        # Создаём тестового пользователя
        self.order_user = User.objects.create_user(
            username="orderuser@example.com",
            email="orderuser@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.order_user) # Аутентификация пользователя

        # Создаём объекты для заказа
        self.category = Category.objects.create(name="Тестовая Категория")
        self.shop = Shop.objects.create(name="Тестовый Магазин", state=True)
        self.product = Product.objects.create(name="Тестовый Товар", category=self.category)
        self.product_info = ProductInfo.objects.create(
            product=self.product,
            shop=self.shop,
            name="Тестовая Инфа",
            price=100.00,
            price_rrc=110.00,
            quantity=2
        )
        # Создание тестового контакта
        self.contact = Contact.objects.create(
            user=self.order_user,
            first_name="Тест_имя",
            last_name="Заказ",
            email="order_test@example.com",
            phone="+70000000000",
            city="Тест",
            street="Тест",
            house_number="1"
        )
        # Подготовим URL-ы
        self.confirm_order_url = reverse("order_confirm_api_v1") # POST /api/v1/confirm-order/
        self.order_history_url = reverse("order_history_api_v1") # GET /api/v1/orders/


    def test_confirm_order_success(self):
        """Тест: успешное подтверждение заказа."""
        # Сначала добавим товар в корзину пользователя
        cart, created = Cart.objects.get_or_create(user=self.order_user)
        CartItem.objects.create(cart=cart, product_info=self.product_info, quantity=2)

        # Подготовка данных для подтверждения
        confirm_data = {
            "cart_id": cart.id,
            "contact_id": self.contact.id
        }
        # Отправим POST-запрос
        response = self.client.post(self.confirm_order_url, confirm_data, format="json")

        # 1. Проверка статуса ответа (201 Created)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 2. Проверка, что заказ создан
        self.assertTrue(Order.objects.filter(user=self.order_user).exists())
        created_order = Order.objects.get(user=self.order_user)
        # 3. Проверка, что в заказе одна позиция
        self.assertEqual(created_order.items.count(), 1)
        order_item = created_order.items.first()
        # 4. Проверка, что позиция заказа связана с правильным товаром и количеством
        self.assertEqual(order_item.product_info, self.product_info)
        self.assertEqual(order_item.quantity, 2)
        # 5. Проверка, что общая сумма заказа соответствует расчету
        expected_total = self.product_info.quantity * self.product_info.price # 2 * 100.00
        self.assertEqual(response.data["total_price"], expected_total)
        # 6. Проверка, что корзина очищена
        self.assertEqual(CartItem.objects.filter(cart=cart).count(), 0)
        # 7. Проверка, что количество на складе уменьшилось
        self.product_info.refresh_from_db()
        self.assertEqual(self.product_info.quantity, 0) # Было 2, добавили 2, стало 0


    def test_get_order_history(self):
        """Тест: получение истории заказов."""
        # Сначала создадим заказ, вызвав confirm_order
        self.test_confirm_order_success() # Подтверждаем заказ

        # Отправляем GET-запрос на эндпоинт истории заказов
        response = self.client.get(self.order_history_url)

        # 1. Проверка, что статус ответа 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2. Проверка, что в истории 1 заказ
        self.assertEqual(len(response.data), 1)
        # 3. Проверка, что данные заказа совпадают (например, статус, дата)
        order_data = response.data[0]
        self.assertEqual(order_data["status"], "new") # По умолчанию при создании заказа статус "new"
        self.assertEqual(order_data["total_price"], 200.00) # Общая сумма
        self.assertEqual(order_data["created_at"], response.data[0]["created_at"]) # Дата создания
        # 4. Проверка, что в заказе есть позиции
        self.assertEqual(len(order_data["items"]), 1)


    def test_get_order_detail(self):
        """Тест: получение деталей конкретного заказа."""
        # Сначала создадим заказ
        self.test_confirm_order_success() # Подтверждаем заказ
        created_order = Order.objects.get(user=self.order_user)

        # Формируем URL для детального доступа к заказу
        order_detail_url = reverse("order_detail_api_v1", kwargs={"order_id": created_order.id})

        # Отправляем GET-запрос на эндпоинт детализации заказа
        response = self.client.get(order_detail_url)

        # 1. Проверка, что статус ответа 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2. Проверка, что ID заказа в ответе совпадает с ID созданного заказа
        self.assertEqual(response.data["id"], created_order.id)
        # 3. Проверка общей суммы
        self.assertEqual(response.data["total_price"], 200.00)
        # 4. Проверка, что в заказе есть позиции
        self.assertEqual(len(response.data["items"]), 1)
  
        # 3. Проверка, что данные заказа совпадают (например, статус, дата)
        item_data = response.data["items"][0]
        self.assertEqual(item_data["product_name"], self.product.name)
        self.assertEqual(item_data["quantity"], 2)
        self.assertEqual(item_data["price"], "100.00")


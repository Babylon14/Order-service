from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from backend.models import (Order, OrderItem, Cart, CartItem, ProductInfo,
                             Shop, Product, Category, Contact)


User = get_user_model()

class OrderAPIViewTestCase(TestCase):
    """Тестирование API заказов."""
    def setUp(self):
        """Настройка тестового клиента и пользователя."""
        self.client = APIClient()
        # Создаём тестового пользователя
        self.user = User.objects.create_user(
            username="orderuser@example.com",
            email="orderuser@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        
        # Создаём объекты для заказа
        self.category = Category.objects.create(name="Тестовая категория")
        self.shop = Shop.objects.create(name="Тестовый магазин",state=True)
        self.product = Product.objects.create(name="Тестовый Товар", category=self.category)
        self.product_info = ProductInfo.objects.create(
            product=self.product,
            shop=self.shop,
            name="Тестовая информация",
            price=100.00,
            quantity=10
        )
        self.contact = Contact.objects.create(
            user=self.user,
            first_name="Тест",
            last_name="Заказ",
            email="order_test@example.com",
            phone="+70000000000",
            city="Тест",
            street="Тест",
            house_number="1"
        )

    def test_confirm_order(self):
        """Тест: подтверждение заказа."""
        # Сначала добавим товар в корзину
        cart, created = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=cart, product_info=self.product_info, quantity=2)

        order_url = reverse("order_confirm_api_v1")
        order_data = {
            "cart_id": cart.id,
            "contact_id": self.contact.id
        }
        response = self.client.post(order_url, order_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Проверка, что заказ создан
        self.assertTrue(Order.objects.filter(user=self.user).exists())
        # Проверка, что корзина очищена
        self.assertEqual(CartItem.objects.filter(cart=cart).count(), 0)
        # Проверка, что количество на складе уменьшилось
        self.product_info.refresh_from_db()
        self.assertEqual(self.product_info.quantity, 8) # Было 10, добавили 2, стало 8


    def test_get_order_history(self):
        """Тест: получение истории заказов."""
        # Создадим заказ (например, через confirm_order или вручную)
        order = Order.objects.create(user=self.user)

        order_url = reverse("order_history_api_v1")
        response = self.client.get(order_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверка, что заказ в списке
        self.assertContains(response, str(order.id))


from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from backend.models import Cart, CartItem, ProductInfo, Shop, Product, Category


User = get_user_model()

class CartAPIViewTestCase(TestCase):
    """Тестирование API-вьюшки Корзины."""
    def setUp(self):
        """Настройка тестового клиента и пользователя."""
        self.client = APIClient()
        # Создаём тестового пользователя
        self.user = User.objects.create_user(
            username="cartuser@example.com",
            email="cartuser@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)
        # Создаём необходимые объекты для тестов Корзины
        self.category = Category.objects.create(name="Тестовая категория")
        self.shop = Shop.objects.create(name="Тестовый магазин",state=True)
        self.product = Product.objects.create(name="Тестовый Товар", category=self.category)
        self.product_info = ProductInfo.objects.create(
            product=self.product,
            shop=self.shop,
            name="Тестовая информация о товаре",
            price=100.00,
            quantity=10
        )

    def test_get_cart_empty(self):
        """Тест: получения пустой Корзины."""
        response = self.client.get(reverse("cart_detail_api_v1"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что корзина пуста
        self.assertEqual(len(response.data["items"]), 0)


    def test_add_item_to_cart(self):
        """Тест: добавление товара в Корзину."""
        url = reverse("cart_item_add_api_v1")
        data = {
            "product_info_id": self.product_info.id,
            "quantity": 2
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["quantity"], 2)
        # Проверка, что товар действительно добавлен в БД
        self.assertEqual(CartItem.objects.filter(
            cart__user=self.user, product_info=self.product_info).count(), 1)


from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from backend.models import Cart, CartItem, ProductInfo, Shop, Product, Category


User = get_user_model()

class CartAPIViewTestCase(APITestCase):
    """Тестирование API-вьюшки Корзины."""
    def setUp(self):
        """Общие настройки тестового клиента и пользователя."""
        # Создаём тестового пользователя
        self.cart_user = User.objects.create_user(
            username="cartuser@example.com",
            email="cartuser@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.cart_user) # Аутентификация пользователя

        # Создаём необходимые объекты для тестов Корзины
        self.category = Category.objects.create(name="Тестовая категория")
        self.shop = Shop.objects.create(name="Тестовый магазин",state=True)
        self.product = Product.objects.create(name="Тестовый Товар", category=self.category)
        self.product_info = ProductInfo.objects.create(
            name="Тестовая информация о товаре",
            product=self.product,
            shop=self.shop,
            price=100.00,
            price_rrc=110.00,
            quantity=2
        )
        # Url-адреса для тестирования
        self.cart_detail_url = reverse("cart_detail_api_v1")  # GET /api/v1/cart/
        self.cart_add_url = reverse("cart_item_add_api_v1")  # POST /api/v1/cart/add/


    def test_get_empty_cart(self):
        """Тест: получения пустой Корзины."""
        # Отправляем GET-запрос на получение данных
        response = self.client.get(self.cart_detail_url)

        # 1. Проверяем статус ответа 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2. Проверяем, что корзина пуста
        self.assertEqual(len(response.data["items"]), 0)
        # 3. Проверяем, что общая сумма равна 0
        self.assertEqual(response.data["total_price"], 0)


    def test_add_item_to_cart(self):
        """Тест: добавление товара в Корзину."""
        # Перед тестом убедимся, что Корзина пуста
        self.assertEqual(Cart.objects.filter(user=self.cart_user).count(), 1) # Корзина создается при первом обращении
        self.assertEqual(CartItem.objects.filter(cart__user=self.cart_user).count(), 0) # Корзина пуста

        cart_data = {
            "product_info_id": self.product_info.id, # ID товара
            "quantity": 2                            # Количество товара
        }
        # Отправляем POST-запрос на добавление товара в Корзину
        response = self.client.post(self.cart_add_url, cart_data, format="json")

        # 1. Проверяем статус ответа 201
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 2. Проверяем, что ответе корректные данные
        self.assertEqual(response.data["product_name"], self.product.name)
        self.assertEqual(response.data["quantity"], 2)
        self.assertEqual(response.data["total_price"], 200.00) # 200.00 * 2 = 400.00

        # 3. Проверим, что товар действительно добавлен в БД
        self.assertEqual(CartItem.objects.filter(
            cart__user=self.cart_user, product_info=self.product_info).count(), 1)
        cart_item = CartItem.objects.get(cart__user=self.cart_user, product_info=self.product_info)
        self.assertEqual(cart_item.quantity, 2)


    def test_add_item_to_cart_update_quantity(self):
        """Тест: добавление товара, который уже есть в корзине (обновление количества)."""
        # Добавление товара
        CartItem.objects.create(
           cart=self.cart_user.cart, 
           product_info=self.product_info,
           quantity=1 
        ) 
        # 1. Проверим начальное количество
        initial_cart_item = CartItem.objects.get(cart__user=self.cart_user, product_info=self.product_info)
        self.assertEqual(initial_cart_item.quantity, 1)

        # Теперь добавим ещё 3 штуки того же товара
        data = {
            "product_info_id": self.product_info.id,
            "quantity": 3
        }
        # Отправляем POST запрос
        response = self.client.post(self.cart_add_url, data, format="json")

        # 2. Проверяем ответ 201
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 3. Проверяем, что количество товара увеличилось: 1 (было) + 3 (добавили) = 4
        self.assertEqual(response.data["quantity"], 4)
        self.assertEqual(response.data["total_price"], 400.00) # 4 * 100.00 = 400.00

        # 4. Проверяем БД
        updated_cart_item = CartItem.objects.get(cart__user=self.cart_user, product_info=self.product_info)
        self.assertEqual(updated_cart_item.quantity, 4)


    def test_update_cart_item_quantity(self):
        """Тест: обновление количества товара в корзине."""
        # Добавляем товар в корзину
        cart_item = CartItem.objects.create(
            cart=self.cart_user.cart,
            product_info=self.product_info,
            quantity=5
        )
        cart_item_id = cart_item.id

        # URL для обновления конкретного элемента
        cart_item_update_url = reverse("cart_item_api_v1", kwargs={"cart_item_id": cart_item_id})

        data = {
            "quantity": 7
        }
        # Отправляем PUT запрос на обновление данных
        response = self.client.put(cart_item_update_url, data, format="json")

        # 1. Проверяем ответ 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2. Проверяем, что количество товара увеличилось: 5 (было) + 2 (добавили) = 7
        self.assertEqual(response.data["quantity"], 7)
        # 3. Проверяем, что общая сумма увеличилась
        self.assertEqual(response.data["total_price"], 700.00) # 7 * 100.00 = 700.00

        # 4. Проверяем БД
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 7)


    def test_delete_cart_item(self):
        """Тест: удаление товара из корзины."""
        # Добавляем товар в корзину
        cart_item = CartItem.objects.create(
            cart=self.user.cart,
            product_info=self.product_info,
            quantity=3
        )
        cart_item_id = cart_item.id

        # URL для удаления конкретного элемента
        cart_item_delete_url = reverse("cart_item_api_v1", kwargs={"cart_item_id": cart_item_id})

        # Отправляем DELETE запрос на удаление данных
        response = self.client.delete(cart_item_delete_url)
        
        # 1. Проверяем ответ 204
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # 2. Проверим, что элемент удален из БД
        self.assertFalse(CartItem.objects.filter(id=cart_item_id).exists())
        # 3. Проверим, что в корзине больше нет этого товара
        self.assertEqual(CartItem.objects.filter(
            cart__user=self.cart_user, product_info=self.product_info).count(), 0)
        

    def test_get_cart_with_items(self):
        """Тест: получение корзины с добавленными товарами."""
        # Добавим несколько товаров
        CartItem.objects.create(
            cart=self.user.cart,
            product_info=self.product_info,
            quantity=2
        )
        # Добавляем ещё один
        another_product_info = ProductInfo.objects.create(
            product=self.product,
            shop=self.shop,
            name="Тестовый Товар 2",
            price=500.00,
            price_rrc=550.00,
            quantity=4
        )
        CartItem.objects.create(
            cart=self.user.cart,
            product_info=another_product_info,
            quantity=1
        )

        # Отправляем GET запрос на получение корзины
        response = self.client.get(self.cart_detail_url)

        # 1. Проверяем ответ 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2. Проверим, что в корзине 2 элемента
        self.assertEqual(len(response.data["items"]), 2)
        # 3. Проверим общую сумму
        expected_total = (2 * 100.00) + (1 * 500.00) # 2 * 100.00 + 1 * 500.00 = 600.00
        self.assertEqual(response.data["total_price"], expected_total)


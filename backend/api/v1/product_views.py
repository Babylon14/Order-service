from rest_framework import generics, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response as DRFResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
import json

from backend.models import Product, ProductInfo
from backend.api.product_serializers import (ProductInfoListSerializer, ProductListSerializer,
                                            ProductImageUploadSerializer)
from backend.api.filters import ProductInfoFilter
from backend.redis_client import get_cache, set_cache


# Время жизни кэша (Time-To-Live). Например, 10 минут.
CACHE_TTL = 60 * 10


class ProductInfoListView(generics.ListAPIView):
    """
    API View для получения списка информации о товарах (ProductInfo)
    с возможностью фильтрации и поиска.
    GET /api/v1/product-infos/
    """
    serializer_class = ProductInfoListSerializer
    permission_classes = [AllowAny]  # Доступно всем пользователям
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Поля для поиска: можно искать по полям ProductInfo и связанным полям Product
    search_fields = [
        "product__name", # Поиск по названию товара
        "description",   # Поиск по описанию из ProductInfo.name
        "shop__name",    # Поиск по названию магазина(поставщика)
        "product_parameters__value", # Поиск по значению параметра
        "product_parameters__parameter__name", # Поиск по названию параметра
    ]
    filterset_class = ProductInfoFilter  # Используем класс фильтров

    # Поля для сортировки
    ordering_fields = [
        "id",           # Сортировка по ID
        "price",         # Сортировка по цене
        "quantity",      # Сортировка по количеству
    ]
    ordering = ["id"]  # Сортировка по умолчанию

    def get_queryset(self):
        """
        Переопределяем метод для получения queryset с предзагрузкой связанных данных
        для оптимизации количества запросов к базе данных.
        """
        return ProductInfo.objects.select_related(
            "product",
            "product__category", # Подгружаем категорию
            "shop",              # Подгружаем магазин
        ).prefetch_related(
            "product_parameters__parameter" # Подгружаем параметры и их имена
        )
    
    def list(self, request, *args, **kwargs):
        """Формирование уникального ключа кэша"""
        # 1. Формирование ключа кэша
        query_params = dict(request.query_params.items())
        query_string = json.dumps(query_params, sort_keys=True)
        cache_key = f"product_list:{query_string}"

        # 2. Попытка получения данных из Redis с помощью нашей функции
        cached_data = get_cache(cache_key)

        if cached_data:
            print("--- CACHE HIT (redis-py): Ответ взят из Redis ---")
            # Возвращаем данные, которые уже являются словарем/списком Python
            return DRFResponse(
                data=cached_data,
                status=200,
                content_type="application/json"
            )
        # 3. Если кэша нет
        print("--- CACHE MISS: Запрос к БД ---")
        response = super().list(request, *args, **kwargs)

        # Если данные успешно получены, сохраняем их
        if response.status_code == 200:
            set_cache(cache_key, response.data, timeout=CACHE_TTL)
            print("--- INFO: Данные сохранены в Redis через redis-py ---")

        return response
            




        # # 3. Попытка получения данных из Redis с помощью Django-кэша
        # cached_data = cache.get(cache_key)

        # if cached_data:
        #     print("--- CACHE HIT: Ответ взят из Django-кэша ---")
        #     return DRFResponse(cached_data, status=200)

        # try:
        #     # Пытаемся сохранить тестовый ключ в базе №1 (наш кэш)
        #     # Если пароль или хост неверны, здесь произойдет сбой (если IGNORE_EXCEPTIONS=False)
        #     # Или вернется False/None (если IGNORE_EXCEPTIONS=True)
        #     success = cache.set('CRITICAL_TEST_KEY_DB_1', 'CONNECTION_OK', timeout=10) 
        #     print(f"DEBUG_REDIS: cache.set() вернул: {success}")
        # except Exception as e:
        #     # Если ошибка все же просочилась, это критично
        #     print(f"DEBUG_REDIS: КРИТИЧЕСКАЯ ОШИБКА: {e}")


        # # 2. Попытка получения закэшированного ответа из Redis
        # cached_content = cache.get(cache_key)

        # if cached_content:
        #     print("--- CACHE HIT: Ответ взят из Redis ---")
        #     return DRFResponse(
        #         data=json.loads(cached_content), # Десериализуем JSON-строку обратно в Python-объект
        #         status=200,
        #         content_type="application/json"
        #     )
        # # Если кэш не нашел ответ, выполняем стандартную логику DRF
        # print("--- CACHE MISS: Запрос к БД ---")
        # # Получаем стандартный ответ от DRF
        # response = super().list(request, *args, **kwargs)

        # # Устанавливаем JSONRenderer
        # response.accepted_renderer = JSONRenderer()
        # # Устанавливаем медиа-тип
        # response.accepted_media_type = "application/json"
        # # Устанавливаем КОНТЕКСТ РЕНДЕРЕРА
        # response.renderer_context = {
        #     "view": self,          # Ссылка на текущее представление
        #     "request": request,    # Объект запроса
        #     "response": response,  # Сам объект ответа
        # }
        # # Принудительно рендерим ответ
        # response.render()
        # Сохраняем финальный объект Response (или его данные) в Redis
        cache.set(cache_key, response.content, timeout=CACHE_TTL)

        return response


class ProductDetailView(generics.RetrieveAPIView):
    """
    API View для получения информации о конкретном товаре по его ID.
    GET /api/v1/products/<int:pk>/
    """
    queryset = Product.objects.all().prefetch_related(
        "product_infos__shop",  # Подгружаем магазин для каждого ProductInfo
        "product_infos__product_parameters__parameter"  # Подгружаем параметры и их имена
    )
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]  # Доступно всем пользователям
    lookup_field = "id"  # Поле, по которому ищем (обычно id)


class ProductImageUploadView(generics.UpdateAPIView):
    """
    API View для обновления (загрузки) изображения конкретного товара по его ID.
    PUT /api/v1/products/<int:pk>/image-upload/
    """
    queryset = Product.objects.all()
    serializer_class = ProductImageUploadSerializer
    permission_classes = [IsAuthenticated]  # Доступно только авторизованным пользователям
    lookup_field = "id"  # Поле, по которому ищем (обычно id)


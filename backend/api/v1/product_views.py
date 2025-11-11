from rest_framework import generics
from rest_framework import filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from backend.models import Product, ProductInfo
from backend.api.product_serializers import ProductInfoListSerializer, ProductListSerializer
from backend.api.filters import ProductInfoFilter


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



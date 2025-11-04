from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from backend.models import Product
from backend.api.product_serializers import ProductListSerializer
from backend.api.filters import ProductFilter


class ProductListView(generics.ListAPIView):
    """
    API View для получения списка товаров с возможностью фильтрации и поиска.
    GET /api/v1/products/
    """
    queryset = Product.objects.all().prefetch_related(
        "category",  # Предзагрузка категорий
        "product_infos__shop",  # Предзагрузка магазинов
        "product_infos__product_parameters__parameter"  # Предзагрузка параметров товаров
    )
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]  # Доступно всем пользователям
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter  # Используем наш класс фильтров
    search_fields = ["name", "product_infos__shop__name"]  # Поля для поиска
    ordering_fields = ["name", "product_infos__price", "product_infos__quantity"]  # Поля для сортировки
    ordering = ["name"]  # Сортировка по умолчанию


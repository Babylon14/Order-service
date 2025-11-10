from rest_framework import generics, status, mixins
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Cart, CartItem, ProductInfo
from backend.api.cart_serializers import CartSerializer, CartItemSerializer


class CartView(generics.RetrieveUpdateDestroyAPIView):
    """
    API View для получения, обновления (очистки) и удаления (очистки) корзины пользователя.
    GET /api/v1/cart/ - получить содержимое корзины
    """
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]  # Только авторизованные пользователи

    def get_object(self):
        """Получает или создает корзину для текущего пользователя."""
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def put(self, request, *args, **kwargs):
        """Обновление(очистка) товара в корзине"""
        cart = self.get_object()
        cart.items.all().delete() # Удаляем все позиции
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def delete(self, request, *args, **kwargs):
        """Удаление товара из корзины"""
        return self.put(request, *args, **kwargs) # Используем ту же логику для delete
    

class CartItemAddView(generics.CreateAPIView):
    """
    API View для добавления товара в корзину или обновления количества.
    POST /api/v1/cart/add/
    Ожидает: {"product_info_id": <id>, "quantity": <int>}
    """
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        product_info_id = request.data.get("product_info_id")
        quantity = request.data.get("quantity", 1)

        try:
            product_info = ProductInfo.objects.get(id=product_info_id)
        except ProductInfo.DoesNotExist:
            return Response({"error": "Товар не найден."}, status=status.HTTP_404_NOT_FOUND)
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_info=product_info,
            defaults={"quantity": quantity}
        )
        if not created:
            # Если товар уже был в корзине, увеличиваем количество
            cart_item.quantity += quantity
            # Проверим, не превышает ли новое количество доступное
            if cart_item.quantity > product_info.quantity:
                cart_item.quantity = product_info.quantity  # Ограничиваем доступным количеством
                # Возвращаем предупреждение
                return Response({
                    "message": f"Количество ограничено доступным запасом: {product_info.quantity}.",
                        "cart_item": CartItemSerializer(cart_item).data}, status=status.HTTP_200_OK
                )
            cart_item.save()

        # Возвращаем обновленную позицию
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    """
    API View для обновления количества или удаления товара из корзины.
    PUT /api/v1/cart/item/<int:id>/ - обновить количество
    DELETE /api/v1/cart/item/<int:id>/ - удалить товар
    """
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id" # Ищем CartItem(Позицию в корзине) по id

    def get_queryset(self):
        """Возвращает queryset только для текущего пользователя."""
        user = self.request.user
        # Получаем корзину пользователя (или None, если её нет)
        # и возвращаем QuerySet позиций из этой корзины
        user_cart = Cart.objects.filter(user=user).first()
        if user_cart:
            return CartItem.objects.filter(cart=user_cart)
        else:
            # Если корзины нет, возвращаем пустой QuerySet
            return CartItem.objects.none()
    
    def put(self, request, *args, **kwargs):
        """Обновление количества."""
        # Вызовем update, который использует get_queryset
        return self.update(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        """Удаление товара."""
        # Вызовем destroy, который использует get_queryset
        return self.destroy(request, *args, **kwargs)
    
    def perform_update(self, serializer):
        """Переопределение perform_update, чтобы проверить доступное количество."""
        instance = serializer.save()
        product_info = instance.product_info
        if instance.quantity > product_info.quantity:
            instance.quantity = product_info.quantity
            instance.save()
            # Возвращаем предупреждение
            return Response({
                "message": f"Количество ограничено доступным запасом: {product_info.quantity}.",
                    "cart_item": CartItemSerializer(instance).data}, status=status.HTTP_200_OK
            )
        

from rest_framework import generics, status
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


class CartItemUpdateView(generics.UpdateAPIView):
    """
    API View для обновления количества товара в корзине.
    PUT /api/v1/cart/item/<int:pk>/ (где pk - id CartItem)
    Ожидает: {"quantity": <int>}
    """
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def perform_update(self, serializer):
        """Переопределяем для проверки доступного кол-ва в корзине."""
        instance = serializer.save()
        product_info = instance.product_info
        if instance.quantity > product_info.quantity:
            instance.quantity = product_info.quantity  # Ограничиваем доступным количеством
            # Возвращаем предупреждение
            return Response({
                "message": f"Количество не может превышать доступный запас: {product_info.quantity}.",
                    "cart_item": CartItemSerializer(instance).data}, status=status.HTTP_200_OK
            )
        

class CartItemDeleteView(generics.DestroyAPIView):
    """
    API View для удаления товара из корзины.
    DELETE /api/v1/cart/item/delete/<int:id>/ (где id - id CartItem)
    """
    queryset = CartItem.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "id"     

        

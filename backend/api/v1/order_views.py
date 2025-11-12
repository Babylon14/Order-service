from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, mixins
from rest_framework.permissions import IsAuthenticated

from backend.models import Cart, Contact, Order, OrderItem
from backend.api.order_serializers import OrderSerializer


class ConfirmOrderView(APIView):
    """
    API View для подтверждения заказа на основе корзины и контакта.
    POST /api/v1/confirm-order/
    Ожидает: {"cart_id": <int>, "contact_id": <int>}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос для подтверждения заказа.
        """
        user = request.user
        cart_id = request.data.get("cart_id")
        contact_id = request.data.get("contact_id")

        if not cart_id or not contact_id:
            return Response({
                "status": "error",
                "message": "cart_id и contact_id обязательны для подтверждения заказа!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Проверяем, существует ли корзина и принадлежит ли она пользователю
        try:
            cart = Cart.objects.prefetch_related('items__product_info').get(id=cart_id, user=user)
        except Cart.DoesNotExist:
            return Response({
                "status": "error",
                "message": f"Корзина с ID {cart_id} не была найдена."},
                status=status.HTTP_404_NOT_FOUND
            )
        # Проверяем, существует ли контакт и принадлежит ли он пользователю
        try:
            contact = Contact.objects.get(id=contact_id, user=user)
        except Contact.DoesNotExist:
            return Response({
                "status": "error",
                "message": f"Контакт с ID {contact_id} не был найден."},
                status=status.HTTP_404_NOT_FOUND
            )
        # Проверяем, пуста ли корзине
        if not cart.items.exists():
            return Response({
                "status": "error",
                "message": "Корзина пуста!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Создаем заказ
        order = Order.objects.create(user=user)

        # Проходим по позициям в корзине
        order_items = []
        for cart_item in cart.items.all():
            product_info = cart_item.product_info
            quantity_in_cart = cart_item.quantity

            # Проверяем, достаточно ли товара в магазине
            if product_info.quantity < quantity_in_cart:
                for item in order_items:
                    item.delete()
                order.delete() # Удаляем заказ
                return Response({
                    "status": "error",
                    "message": f"Недостаточно товара {product_info.product.name} в магазине!"
                            f"Доступно: {product_info.quantity}, запрошено: {quantity_in_cart}."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Создаём OrderItem
            order_item = OrderItem.objects.create(
                order=order,
                product_info=product_info,
                quantity=quantity_in_cart
            )
            order_items.append(order_item)

            # Уменьшаем количество товара в магазине
            product_info.quantity -= quantity_in_cart
            product_info.save()
        
        # Очищаем корзину
        cart.items.all().delete()
        cart.save()

        # Сериализуем и возвращаем заказ
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        

class OrderHistoryView(generics.GenericAPIView, mixins.ListModelMixin):
    """
    API View для получения истории заказов пользователя.
    GET /api/v1/orders/
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает список заказов, принадлежащих текущему пользователю,
        отсортированный по дате создания (новые первыми).
        """
        return Order.objects.filter(
            user=self.request.user).prefetch_related("items__product_info")
        
    def get(self, request, *args, **kwargs):
        # Вызываем метод из ListModelMixin
        return self.list(request, *args, **kwargs)


class OrderDetailView(generics.GenericAPIView, mixins.RetrieveModelMixin):
    """
    API View для получения деталей КОНКРЕТНОГО заказа.
    GET /api/v1/orders/<int:id>/ 
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "id"

    def get_queryset(self):
        """
         Возвращает объекты заказов, принадлежащих текущему пользователю.
        """
        return Order.objects.filter(
            user=self.request.user).prefetch_related("items__product_info")
    
    def get(self, request, *args, **kwargs):
        # Вызываем метод из RetrieveModelMixin
        return self.retrieve(request, *args, **kwargs)







from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import send_mail
from django.conf import settings

from backend.models import Contact, ContactConfirmation
from backend.api.contact_serializers import ContactSerializer
from backend.tasks import send_contact_confirmation_email_task


class ContactListView(generics.ListCreateAPIView):
    """
    API View для получения списка контактов пользователя и создания нового контакта.
    GET /api/v1/contacts/ - получить список контактов
    POST /api/v1/contacts/ - создать новый контакт
    """
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Возвращает список контактов, принадлежащих текущему пользователю."""
        return Contact.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Сохраняет контакт, принадлежащий текущему пользователю."""
        serializer.save(user=self.request.user)


class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API View для получения, обновления и удаления КОНКРЕТНОГО контакта.
    GET /api/v1/contacts/<int:id>/ - получить контакт
    PUT /api/v1/contacts/<int:id>/ - обновить контакт
    PATCH /api/v1/contacts/<int:id>/ - частично обновить контакт
    DELETE /api/v1/contacts/<int:id>/ - удалить контакт
    """
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id" # Используем "id" вместо "pk"

    def get_queryset(self):
        """
        Возвращает список контактов, принадлежащих текущему пользователю.
        Это означает, что пользователь может управлять только своими контактами.
        """
        return Contact.objects.filter(user=self.request.user)


class SendConfirmationEmailView(generics.CreateAPIView):
    """
    API View для отправки письма с подтверждением контакта.
    POST /api/v1/send-contact-confirmation/
    Ожидает: {"contact_id": <int>}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос для отправки письма с подтверждением контакта."""
        import time
        start_time = time.perf_counter() # Записываем время начала выполнения

        user = request.user
        contact_id = request.data.get("contact_id")

        if not contact_id:
            return Response(
                {
                "status": "error",
                "message": "contact_id обязательны для отправки письма с подтверждением!"
                }, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            contact = Contact.objects.get(id=contact_id, user=user)
        except Contact.DoesNotExist:
            return Response(
                {
                "status": "error",
                "message": f"Контакт с ID {contact_id} не был найден."
                }, status=status.HTTP_404_NOT_FOUND
            )
        # Удаляем старый токен 
        ContactConfirmation.objects.filter(contact=contact).delete()

        # Создаем новый токен подтверждения
        confirmation = ContactConfirmation.objects.create(contact=contact)

        # --- ЗАМЕРЯЕМ ВРЕМЯ ОТПРАВКИ EMAIL ---
        email_start_time = time.perf_counter()

        # Запускаем асинхронную задачу для отправки email-письма
        send_contact_confirmation_email_task.delay(contact.id, str(confirmation.token))
        email_end_time = time.perf_counter()
        email_duration = email_end_time - email_start_time
        print(f"[DEBUG] время отправки письма: {email_duration:.4f} секунд")
        # --- КОНЕЦ ЗАМЕРА ---

        end_time = time.perf_counter() # Записываем время окончания выполнения
        total_duration = end_time - start_time
        print(f"[DEBUG] Общее время выполнения запроса: {total_duration:.4f} секунд")

        return Response(
            {"message": f"Письмо с подтверждением отправлено на {contact.email}."},
            status=status.HTTP_200_OK
        )


class ConfirmContactView(APIView):
    """
    API View для подтверждения контакта.
    POST /api/v1/confirm-contact/<uuid:token>/ - подтвердить контакт
    """

    permission_classes = [AllowAny]

    def get(self, request, token, *args, **kwargs):
        try:
            # select_related улучшает производительность, сразу загружая связанный контакт
            confirmation = ContactConfirmation.objects.select_related("contact").get(token=token)
        except ContactConfirmation.DoesNotExist:
            return Response(
                {
                "status": "error",
                "message": "Неверный или истёкший токен подтверждения."
                }, status=status.HTTP_400_BAD_REQUEST
            )
        if confirmation.is_expired():
            confirmation.delete() # Удаляем истёкший токен
            return Response(
                {
                "status": "error",
                "message": "Токен подтверждения истек."
                }, status=status.HTTP_400_BAD_REQUEST
            )
        # Подтверждаем контакт
        contact = confirmation.contact
        contact.is_confirmed = True
        contact.save()

        # Удаляем токен подтверждения после использования
        confirmation.delete()
        return Response(
            {
            "status": "success",
            "message": "Контакт успешно подтверждён!"
            }, status=status.HTTP_200_OK
        )
        
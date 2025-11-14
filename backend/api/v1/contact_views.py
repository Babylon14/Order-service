from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings

from backend.models import Contact, ContactConfirmation
from backend.api.contact_serializers import ContactSerializer


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
        """
        Обрабатывает POST-запрос для отправки письма с подтверждением контакта.
        """
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

        # Отправляем письмо
        self.send_contact_confirmation_email_task(contact, confirmation.token)
        return Response(
            {"message": f"Письмо с подтверждением отправлено на {contact.email}."},
            status=status.HTTP_200_OK
        )

    def send_contact_confirmation_email_task(self, contact, token):
        """Отправляет письмо со ссылкой для подтверждения контакта."""
        # Ссылка для подтверждения, которая ведет на эндпоинт активации)
        confirmation_link = f"http://localhost:8000/api/v1/confirm-contact/{token}/"
        
        subject = "Подтверждение адреса доставки"
        message = f"""
        Здравствуйте, {contact.first_name or contact.user.username}!

        Вы указали этот email ({contact.email}) как адрес доставки.
        Пожалуйста, подтвердите его, перейдя по ссылке:

        {confirmation_link}

        Ссылка действительна в течение 24-х часов.

        С уважением,
        Администрация сервиса.
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [contact.email],
            fail_silently=False,
        )
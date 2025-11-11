from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from backend.models import Contact
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


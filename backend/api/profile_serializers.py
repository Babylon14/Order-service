from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля пользователя."""

    class Meta:
        model = User
        # Поля, которые пользователь может обновлять
        fields = (
            "id", 
            "email",    
            "first_name", 
            "last_name",
            "user_type", 
            "original_avatar",     # Разрешаем загрузку нового файла
            "avatar_thumbnail",    # Для чтения: чтобы фронтенд сразу видел новый URL миниатюры
        )
        read_only_fields = ("id", "user_type", "avatar_thumbnail")

    def validate_email(self, value):
        """ Проверка, что новый email не занят другим пользователем"""
        user = self.context["request"].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Этот email уже занят другим пользователем.")
        return value



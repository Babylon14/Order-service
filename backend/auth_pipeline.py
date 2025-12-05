"""Перехват создания сессии, создание токенов JWT и перенаправление на фронтенд"""
from rest_framework_simplejwt.tokens import RefreshToken


def generate_jwt_token(user, backend, details, response, *args, **kwargs):
    """
    Пайплайн, который выполняется после успешной аутентификации.
    Создает JWT токены для пользователя и добавляет их в сессию, чтобы
    затем использовать их для перенаправления на фронтенд.
    """
    if user:
        print(f"--- ГЕНЕРАЦИЯ ТОКЕНА ДЛЯ ПОЛЬЗОВАТЕЛЯ: {user.username} ---")
        # Создание JWT токенов
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Сохранение токенов в сессии
        kwargs["request"].session["access_token"] = access_token
        kwargs["request"].session["refresh_token"] = refresh_token

        return None # Возврат None продолжает пайплайн
    return None # Если пользователя не удалось создать/найти, продолжаем обычный процесс


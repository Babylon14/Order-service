from django.shortcuts import redirect
from django.conf import settings
from django.views import View

class SocialAuthTokenRedirectView(View):
    """
    Перенаправляет на фронтенд с токенами после успешной аутентификации.
    """
    def get(self, request, *args, **kwargs):
        # Получаем токены, сохраненные в сессии кастомным пайплайном
        access_token = request.session.pop("access_token", None)
        refresh_token = request.session.pop("refresh_token", None)

        # URL фронтенда (всё ещё должен быть http://127.0.0.1:3000 или подобное)
        from django.conf import settings # Импорт settings
        frontend_url = getattr(
            settings, "FRONTEND_SOCIAL_LOGIN_SUCCESS_URL", "http://127.0.0.1:3000/social-login-success"
        )

        if access_token and frontend_url:
            # Строим URL для перенаправления с токенами в параметрах
            full_redirect_url = f"{frontend_url}?access_token={access_token}&refresh_token={refresh_token}"
            print(f"--- ФИНАЛЬНОЕ ПЕРЕНАПРАВЛЕНИЕ НА: {full_redirect_url} ---") # Для отладки
            return redirect(full_redirect_url)
        else:
            print("--- ТОКЕНЫ НЕ НАЙДЕНЫ В СЕССИИ ---") # Для отладки
            # Если что-то пошло не так, перенаправляем на страницу ошибки или главную
            return redirect(settings.LOGIN_URL or "/")


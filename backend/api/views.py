from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError


def index(request):
    """Приветствие на главной странице backend приложения."""
    return HttpResponse(
        "<h1>Hello, this is the backend index page.</h1><p>Welcome to the backend!</p>"
    )


def categories(request):
    """Страница категорий товаров в backend приложении."""
    return HttpResponse(
        "<h1>Страница категорий товаров</h1><p>Здесь будут категории товаров.</p>"
    )


def page_not_found(request, exception):
    """Кастомная страница 404 ошибки."""
    return HttpResponseNotFound(
        "<h1>404 - Страница не найдена</h1><p>Извините, запрашиваемая страница не существует.</p>"
    )


def server_error(request):
    """Кастомная страница 500 ошибки."""
    return HttpResponseServerError(
        "<h1>500 - Внутренняя ошибка сервера</h1><p>Извините, произошла ошибка на сервере.</p>"
    )




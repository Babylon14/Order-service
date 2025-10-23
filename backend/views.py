from django.shortcuts import render, HttpResponse


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


from urllib.request import Request
from django.shortcuts import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound, HttpResponseServerError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Shop
from .utils import load_shop_data_from_yaml


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


@api_view(["POST"])
def import_shop_data_api(request: Request, shop_id=None) -> Response:
    """
    API View для запуска импорта данных магазина из YAML-файла.
    Может принимать shop_id в URL или в теле запроса.
    """
    request_shop_id = shop_id
    if request_shop_id is None:
        request_shop_id = request.data.get("shop_id")

    if request_shop_id is None:
        return Response(
            {"status": "error", "message": "shop_id не предоставлен."},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        shop = Shop.objects.get(id=request_shop_id)
    except ObjectDoesNotExist:
        return Response(
            {"status": "error", "message": f"Магазин с ID {request_shop_id} не найден."},
            status=status.HTTP_404_NOT_FOUND
        )
    yaml_file_path = shop.get_source_file_path()
    result = load_shop_data_from_yaml(shop_id=shop.id, yaml_file_path=yaml_file_path)
    if result and result.get("status") == "success":
        return Response(result, status=status.HTTP_200_OK)
    else:
        error_message = result.get(
            "message", "Неизвестная ошибка при импорте данных."
            ) if result else "Неизвестная ошибка при импорте данных."
        return Response(
            {"error": error_message},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(["POST"])
def import_all_shops_data_api(request: Request) -> Response:
    """
    API View для запуска импорта данных *всех* магазинов из их YAML-файлов.
    """
    shops = Shop.objects.filter(state=True)
    results = []
    success_count = 0
    error_count = 0

    for shop in shops:
        yaml_file_path = shop.get_source_file_path()
        result = load_shop_data_from_yaml(shop_id=shop.id, yaml_file_path=yaml_file_path)
        if result and result.get("status") == "success":
            success_count += 1
            results.append({
                "shop_id": shop.id,
                "shop_name": shop.name,
                "status": "success",
                "details": result.get("message", "")
            })
        else:
            error_count += 1
            error_message = result.get(
                "message", "Ошибка при импорте данных."
            ) if result else "Неизвестная ошибка при импорте данных."
            results.append({
                "shop_id": shop.id,
                "shop_name": shop.name,
                "status": "error",
                "details": error_message
            })
    overall_status = "partial_success" if success_count > 0 and error_count > 0 else (
        "success" if success_count > 0 else "error"
    )
    return Response({"overall_status": overall_status,
        "summary": f'Загружено: {success_count}, Ошибок: {error_count}',
        "results": results
    }, status=status.HTTP_200_OK if success_count > 0 else status.HTTP_500_INTERNAL_SERVER_ERROR)



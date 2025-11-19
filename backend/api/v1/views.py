from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from backend.models import Shop
from backend.tasks import import_all_shops_data_task, import_shop_data_task


# --- API View-класс для запуска импорта ВСЕХ магазинов ---
class StartImportAllShopsView(APIView):
    """
    API View для запуска асинхронного импорта данных *ВСЕХ* активных магазинов.
    POST /api/v1/start-import-all-shops/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        task = import_all_shops_data_task.delay() # Запускаем Celery-задачу
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED) # Возвращаем id задачи


# --- Класс для запуска импорта КОНКРЕТНОГО магазина ---
class StartImportShopView(APIView):
    """
    API View для запуска асинхронного импорта данных КОНКРЕТНОГО магазина.
    POST /api/v1/start-import-shop/<int:shop_id>/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, shop_id, *args, **kwargs):
        yaml_file_path = request.data.get("yaml_file_path")
        task = import_shop_data_task.delay(shop_id, yaml_file_path) # Запускаем Celery-задачу
        return Response(
            {"task_id": task.id, "message": f"Импорт магазина {shop_id} начат."},
            status=status.HTTP_202_ACCEPTED
        ) # Возвращаем id задачи



# # --- API Views для импорта данных из YAML-файлов ---
# @api_view(["POST"])
# def import_shop_data_api(request: Request, shop_id=None) -> Response:
#     """
#     API View для запуска импорта данных магазина из YAML-файла.
#     Может принимать shop_id в URL или в теле запроса.
#     """
#     request_shop_id = shop_id
#     if request_shop_id is None:
#         request_shop_id = request.data.get("shop_id")

#     if request_shop_id is None:
#         return Response(
#             {"status": "error", "message": "shop_id не предоставлен."},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#     try:
#         shop = Shop.objects.get(id=request_shop_id)
#     except ObjectDoesNotExist:
#         return Response(
#             {"status": "error", "message": f"Магазин с ID {request_shop_id} не найден."},
#             status=status.HTTP_404_NOT_FOUND
#         )
#     yaml_file_path = shop.get_source_file_path()
#     result = load_shop_data_from_yaml(shop_id=shop.id, yaml_file_path=yaml_file_path)
#     if result and result.get("status") == "success":
#         return Response(result, status=status.HTTP_200_OK)
#     else:
#         error_message = result.get(
#             "message", "Неизвестная ошибка при импорте данных."
#             ) if result else "Неизвестная ошибка при импорте данных."
#         return Response(
#             {"error": error_message},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )
    
# @api_view(["POST"])
# def import_all_shops_data_api(request: Request) -> Response:
#     """
#     API View для запуска импорта данных *всех* магазинов из их YAML-файлов.
#     """
#     shops = Shop.objects.filter(state=True)
#     results = []
#     success_count = 0
#     error_count = 0

#     for shop in shops:
#         yaml_file_path = shop.get_source_file_path()
#         result = load_shop_data_from_yaml(shop_id=shop.id, yaml_file_path=yaml_file_path)
#         if result and result.get("status") == "success":
#             success_count += 1
#             results.append({
#                 "shop_id": shop.id,
#                 "shop_name": shop.name,
#                 "status": "success",
#                 "details": result.get("message", "")
#             })
#         else:
#             error_count += 1
#             error_message = result.get(
#                 "message", "Ошибка при импорте данных."
#             ) if result else "Неизвестная ошибка при импорте данных."
#             results.append({
#                 "shop_id": shop.id,
#                 "shop_name": shop.name,
#                 "status": "error",
#                 "details": error_message
#             })
#     overall_status = "partial_success" if success_count > 0 and error_count > 0 else (
#         "success" if success_count > 0 else "error"
#     )
#     return Response({"overall_status": overall_status,
#         "summary": f'Загружено: {success_count}, Ошибок: {error_count}',
#         "results": results
#     }, status=status.HTTP_200_OK if success_count > 0 else status.HTTP_500_INTERNAL_SERVER_ERROR)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from celery.result import AsyncResult

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
        return Response(
            {"task_id": task.id, "message": "Импорт всех магазинов начат."},
            status=status.HTTP_202_ACCEPTED
        )


# --- API View-класс для запуска импорта КОНКРЕТНОГО магазина ---
class StartImportShopView(APIView):
    """
    API View для запуска асинхронного импорта данных КОНКРЕТНОГО магазина.
    POST /api/v1/start-import-shop/<int:shop_id>/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, shop_id, *args, **kwargs):
        shop = get_object_or_404(Shop, id=shop_id) # Проверяем существование магазина
        yaml_file_path = request.data.get("yaml_file_path") # Получаем путь к YAML-файлу
        task = import_shop_data_task.delay(shop_id, yaml_file_path) # Запускаем Celery-задачу

        return Response(
            {"task_id": task.id, "message": f"Импорт магазина {shop.name} начат."},
            status=status.HTTP_202_ACCEPTED
        )


# --- Класс для получения статуса задачи ---
class GetImportStatusView(APIView):
    """
    API View для получения статуса асинхронной задачи импорта.
    GET /api/v1/import-status/<task_id>/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id, *args, **kwargs):
        task_result = AsyncResult(task_id)
        
        if task_result.state == "PENDING": # Если задача еще не запущена
            response = {
                "state": task_result.state,
                "status": "Задача ещё не запущена..."
            }
        elif task_result.state == "PROGRESS": # Если задача выполняется
            response = {
                "state": task_result.state,
                "status": "Задача выполняется..."
            }
        elif task_result.state == "SUCCESS": # Если задача завершена успешно
            response = {
                "state": task_result.state,
                "status": "Задача завершена успешно",
                "message": task_result.result
            }
        elif task_result.state == "FAILURE": # Если задача завершена с ошибкой
            response = {
                "state": task_result.state,
                "status": "Задача завершена с ошибкой",
                "message": str(task_result.info)
            }
        else: # Если другие состояния
            response = {
                "state": task_result.state,
                "status": str(task_result.info),
            }

        return Response(response)


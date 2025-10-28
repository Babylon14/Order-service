import yaml
from django.db import transaction
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter


def load_shop_data_from_yaml(shop_id: int, yaml_file_path: str) -> dict:
    """
    Загружает данные магазина из YAML-файла и обновляет/создает соответствующие модели Django.
    Args:
        shop_id (int): ID магазина в базе данных.
        yaml_file_path (str): Путь к YAML-файлу с данными.
    """
    try:
        shop = Shop.objects.get(id=shop_id)
    except Shop.DoesNotExist:
        print(f"Ошибка: магазин с {shop_id} не существует.")
        return

    try:
        with open(yaml_file_path, "r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Ошибка: файл {yaml_file_path} не найден.")
        return
    except yaml.YAMLError as err:
        print(f"Ошибка при чтении YAML-файла: {err}")
        return  

    with transaction.atomic():
        """Транзакция для обеспечения целостности данных."""
        _process_categories(yaml_data.get("categories", []), shop)
        _process_products(yaml_data.get("products", []), shop)
        _process_product_infos(yaml_data.get("product_infos", []), shop)
        _process_product_parameters(yaml_data.get("product_parameters", []), shop)




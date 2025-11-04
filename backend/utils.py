import yaml
from django.db import transaction
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter
import logging


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
        print(f"Ошибка: магазин с ID {shop_id} не существует.")
        return {"status": "error", "message": f"Магазин с ID {shop_id} не был найден."}

    try:
        with open(yaml_file_path, "r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Ошибка: файл {yaml_file_path} не найден.")
        return {"status": "error", "message": f"Файл {yaml_file_path} не найден."}
    except yaml.YAMLError as err:
        print(f"Ошибка при чтении YAML-файла: {err}")
        return {"status": "error", "message": f"Ошибка YAML: {err}"}

    if not isinstance(yaml_data, dict):
        print("Ошибка: YAML-файл должен содержать объект словарь.")
        return {"status": "error", "message": "Неверный формат YAML-файла."}

    try:
        with transaction.atomic():
            """Транзакция для обеспечения целостности данных."""
            _process_categories(yaml_data.get("categories", []), shop)
    except Exception as err:
        logging.exception(f"Ошибка при загрузке данных из {yaml_file_path} для магазина {shop.name}: {err}")
        print(f"Ошибка при загрузке данных из {yaml_file_path} для магазина {shop.name}: {err}")
        return {"status": "error", "message": f"Ошибка при загрузке данных: {err}"}

     # Возвращаем успешный статус
    return {
        "status": "success",
        "message": f"Данные из {yaml_file_path} успешно загружены для магазина {shop.name}."
    }


def _process_categories(categories_data: list, shop: Shop) -> None:
    """Обрабатывает категории из YAML-данных и связывает их с магазином."""
    for category_data in categories_data:
        cat_name = category_data.get("name")
        cat_description = category_data.get("description", "")

        if not cat_name:
            print("Пропущена категория без имени.")
            continue

        # Получаем или создаем категорию
        category, created = Category.objects.get_or_create(
            name=cat_name,
            defaults={"description": cat_description}
        )
        if not created:
            category.description = cat_description
            category.save()

        # Добавляем магазин к категории, если его там еще нет
        category.shops.add(shop)

        # Обрабатываем товары в категории
        _process_products(category_data.get("products", []), category, shop)


def _process_products(products_data: list, category: Category, shop: Shop) -> None:
    """Обрабатывает товары из YAML-данных и связывает их с категорией и магазином."""
    for product_data in products_data:
        prod_name = product_data.get("name")

        if not prod_name:
            print("Пропущен товар без имени.")
            continue

        # Получаем или создаем товар
        product, created = Product.objects.get_or_create(
            name=prod_name,
            defaults={"category": category}
        )

        # Если продукт уже существовал, но не был в нужной категории, обновим его категорию
        if not created and product.category != category:
            product.category = category
            product.save()

        # Обрабатываем информацию о продукте
        _process_product_infos(product_data.get("product_infos", []), product, shop)


def _process_product_infos(product_infos_data: list, product: Product, shop: Shop) -> None:
    """
    Обрабатывает информацию о продукте (цена, количество и т.д.)
    из YAML-данных и связывает ее с продуктом и магазином.
    """
    for info_data in product_infos_data:
        info_name = info_data.get("name")
        price = info_data.get("price")
        price_rrc = info_data.get("price_rrc")
        quantity = info_data.get("quantity")

        if not all([info_name, price, price_rrc, quantity]):
            print(f"Пропущена информация о продукте '{info_name}' из-за отсутствующих данных.")
            continue

        # Получаем или создаем информацию о продукте
        product_info, created = ProductInfo.objects.get_or_create(
            product=product,
            shop=shop,
            name=info_name,
            defaults={"price": price, "price_rrc": price_rrc, "quantity": quantity}
        )

        # Если объект уже существовал, обновляем поля
        if not created:
            product_info.price = price
            product_info.price_rrc = price_rrc
            product_info.quantity = quantity
            product_info.save()

        # Обрабатываем параметры продукта
        _process_product_parameters(info_data.get("parameters", []), product_info)


def _process_product_parameters(parameters_data: list, product_info: ProductInfo) -> None:
    """Обрабатывает параметры продукта из YAML-данных и связывает их с информацией о продукте."""
    for param_data in parameters_data:
        param_name = param_data.get("name")
        param_value = param_data.get("value")

        if not all([param_name, param_value]):
            print(f"Пропущен параметр {product_info.product.name} из-за отсутствующих данных.")
            continue

        # Получаем или создаем параметр
        parameter, _ = Parameter.objects.get_or_create(name=param_name)

        # Создаем или обновляем связь между информацией о продукте и параметром
        ProductParameter.objects.update_or_create(
            product_info=product_info,
            parameter=parameter,
            defaults={"value": param_value}
        )


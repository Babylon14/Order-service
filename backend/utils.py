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


def _process_products(products_data: list, shop: Shop, category: Category) -> None:
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
        _process_product_infos(product_data.get("product_info", []), product, shop)


def _process_product_infos(product_infos_data: list, product: Product, shop: Shop) -> None:
    """
    Обрабатывает информацию о продукте (цена, количество и т.д.)
    из YAML-данных и связывает ее с продуктом и магазином.
    """
    pass






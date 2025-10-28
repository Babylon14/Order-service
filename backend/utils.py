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
    for info_data in product_infos_data:
        info_name = info_data.get("name")
        price = info_data.get("price")
        price_rcc = info_data.get("price_rcc")
        quantity = info_data.get("quantity")

        if not all([info_name, price, price_rcc, quantity]):
            print(f"Пропущена информация о продукте '{info_name}' из-за отсутствующих данных.")
            continue

        # Получаем или создаем информацию о продукте
        product_info, created = ProductInfo.objects.get_or_create(
            product=product,
            shop=shop,
            name=product.name,
            defaults={"price": price, "price_rcc": price_rcc, "quantity": quantity}
        )

        # Если объект уже существовал, обновляем поля
        if not created:
            product_info.price = price
            product_info.price_rcc = price_rcc
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
        parameter, created = Parameter.objects.get_or_create(name=param_name)

        # Создаем или обновляем связь между информацией о продукте и параметром
        ProductParameter.objects.update_or_create(
            product_info=product_info,
            parameter=parameter,
            defaults={"value": param_value}
        )


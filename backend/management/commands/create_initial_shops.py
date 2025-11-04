from django.core.management.base import BaseCommand
from backend.models import Shop


class Command(BaseCommand):
    help = "Создает начальные записи магазинов в базе данных."

    def handle(self, *args, **options):
        initial_shops = [
            {"name": "shop1", "source_file": "data/shop1.yaml"},
            {"name": "shop2", "source_file": "data/shop2.yaml"},
            {"name": "shop3", "source_file": "data/shop3.yaml"},
        ]

        created_count = 0
        for shop_info in initial_shops:
            shop, created = Shop.objects.get_or_create(
                name=shop_info["name"],
                defaults={
                    "source_file": shop_info["source_file"],
                    "state": shop_info["state"] if "state" in shop_info else True,
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Магазин '{shop.name}' (ID: {shop.id}) успешно создан.")
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f"Магазин '{shop.name}' (ID: {shop.id}) уже существовал.")
                )
        if created_count == 0:
            self.stdout.write(
                self.style.WARNING("Новых магазинов не было создано.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Процесс завершен. Создано {created_count} новых магазинов.")
            )







import json
import os
from django.conf import settings
from products.models import Product
from catalog.models import Catalog


def process_product(file_path):
    """функция обрабатывает данные из файла и создает или обновляет товары"""
    with open(file_path, encoding="utf-8") as file:
        data = json.load(file)
    log_file_name = os.path.basename(file_path) + ".log"
    log_file_path = os.path.join(settings.IMPORT_LOGS, log_file_name)
    with open(log_file_path, "w", encoding="utf-8") as log_file:
        errors = []
        products = []  # создаем пустой список для товаров
        for item in data:
            name = item.get("name")
            description = item.get("description")
            limited_edition = item.get("limited_edition")
            preview = item.get("preview")
            category = item.get("category")
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    "name": name,
                    "description": description,
                    "limited_edition": limited_edition,
                    "preview": preview,
                },
            )
            if not created:
                product.name = name
                product.description = description
                product.limited_edition = limited_edition
                product.preview = preview
                product.save()
            category, _ = Catalog.objects.get_or_create(name=category)
            product.category = category
            product.save()
            products.append(product)
            log_file.write(f'Товар {name} был {"создан" if created else "обновлен"}\n')
    return products, errors

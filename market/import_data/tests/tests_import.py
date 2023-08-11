import os
from django.test import TestCase
from products.models import Product
from catalog.models import Catalog
from import_data.services import process_product


class ImportTestCase(TestCase):
    """класс для тестирования запуска импорта"""

    def setUp(self):
        self.file_path = "test_imp.json"
        self.abs_file = os.path.join(".", "import_data/fixtures", self.file_path)

    def test_process_products(self):
        """Вызываем функцию process_products"""
        products, errors = process_product(self.abs_file)

        # Проверяем, что список ошибок пустой
        self.assertFalse(errors)

        # Проверяем, что длина списка товаров равна ожидаемому количеству импортированных товаров
        self.assertEqual(len(products), 2)

        # Проверяем, что товары имеют правильные атрибуты
        product1 = products[0]
        self.assertEqual(product1.name, "Ноутбук ASUS VivoBook 15")
        self.assertEqual(
            product1.description,
            "Ноутбук ASUS VivoBook 15 с диагональю экрана 15.6 дюйма, процессором Intel Core i5.",
        )
        self.assertEqual(product1.limited_edition, True)
        self.assertEqual(product1.preview, "preview1.png")
        self.assertEqual(product1.category.name, "Ноутбуки")

        product2 = products[1]
        self.assertEqual(product2.name, "Смартфон Samsung Galaxy S21")
        self.assertEqual(product2.description, "Description 2")
        self.assertEqual(product2.limited_edition, False)
        self.assertEqual(product2.preview, "preview2.png")
        self.assertEqual(product2.category.name, "Смартфоны")

        # Проверяем, что записи о товарах были созданы в базе данных
        self.assertTrue(Product.objects.filter(name="Ноутбук ASUS VivoBook 15").exists())
        self.assertTrue(Product.objects.filter(name="Смартфон Samsung Galaxy S21").exists())
        self.assertTrue(Catalog.objects.filter(name="Ноутбуки").exists())
        self.assertTrue(Catalog.objects.filter(name="Смартфоны").exists())

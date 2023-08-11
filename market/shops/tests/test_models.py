from django.test import TestCase

from shops.models import Shop, Offer
from products.models import Product, Property
from users.models import CustomUser


class ShopModelTest(TestCase):
    """Класс тестов модели Магазин"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.property = Property.objects.create(name="тестовая характеристика")
        cls.product = Product.objects.create(
            name="тестовый продукт",
        )
        cls.product.property.set([cls.property])
        cls.user = CustomUser.objects.create(username="User_test", password="123")
        cls.shop = Shop.objects.create(name="тестовый магазин", user=cls.user)
        cls.offer = Offer.objects.create(shop=cls.shop, product=cls.product, price=25)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        ShopModelTest.property.delete()
        ShopModelTest.product.delete()
        ShopModelTest.shop.delete()
        ShopModelTest.offer.delete()
        ShopModelTest.user.delete()

    def test_verbose_name(self):
        shop = ShopModelTest.shop
        field_verboses = {
            "name": "название",
            "products": "товары в магазине",
            "user": "пользователь",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(shop._meta.get_field(field).verbose_name, expected_value)

    def test_name_max_length(self):
        shop = ShopModelTest.shop
        max_length = shop._meta.get_field("name").max_length
        self.assertEqual(max_length, 512)


class OfferModelTest(TestCase):
    """Класс тестов модели Предложение магазина"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = Product.objects.create(
            name="тестовый продукт",
        )
        cls.user = CustomUser.objects.create(username="User_test", password="123")
        cls.shop = Shop.objects.create(name="тестовый магазин", user=cls.user)
        cls.offer = Offer.objects.create(shop=cls.shop, product=cls.product, price=35)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        OfferModelTest.product.delete()
        OfferModelTest.shop.delete()
        OfferModelTest.offer.delete()
        OfferModelTest.user.delete()

    def test_verbose_name(self):
        offer = OfferModelTest.offer
        field_verboses = {
            "price": "цена",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(offer._meta.get_field(field).verbose_name, expected_value)

    def test_price_max_digits(self):
        offer = OfferModelTest.offer
        max_digits = offer._meta.get_field("price").max_digits
        self.assertEqual(max_digits, 10)

    def test_price_decimal_places(self):
        offer = OfferModelTest.offer
        decimal_places = offer._meta.get_field("price").decimal_places
        self.assertEqual(decimal_places, 2)

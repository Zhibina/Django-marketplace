from django.test import TestCase
from unittest.mock import MagicMock
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from discounts.models import ShopItemDiscount, CartItemDiscount
from discounts.forms import ShopDiscountCreationForm, CartDiscountCreationForm
from discounts.services.discountservice import DiscountService
from products.models import Product
from catalog.models import Catalog
from cart.cart import Cart


class DiscountCreateModel(TestCase):
    """Класс тестов для модели скидок"""

    fixtures = [
        "fixtures/010_auth_group.json",
        "fixtures/011_users.json",
        "fixtures/015_shops_banner.json",
        "fixtures/020_catalog_categories.json",
        "fixtures/025_products.json",
        "fixtures/026_tags.json",
        "fixtures/027_product_image.json",
        "fixtures/030_property.json",
        "fixtures/035_productproperty.json",
        "fixtures/040_shops.json",
        "fixtures/045_offers.json",
        "fixtures/075_discounts_shop_item_discount.json",
        "fixtures/080_discounts_cart_item_discount.json",
    ]

    @classmethod
    def setUpClass(cls):
        """Установка необходимых значений"""
        super().setUpClass()
        cls.products = Product.objects.all()
        cls.categories = Catalog.objects.all()
        cls.date_now = timezone.now()
        cls.nex_date = cls.date_now + timezone.timedelta(days=1)
        cls.shop_discount_form = ShopDiscountCreationForm
        cls.cart_discount_form = CartDiscountCreationForm

    @classmethod
    def tearDownClass(cls):
        """Удаление установленных значений"""
        super().tearDownClass()
        cls.products.delete()
        cls.categories.delete()

    def test_create_shop_item_discount_success(self):
        """Создание записи скидки для товаров в магазине в таблицу через форму"""
        form_data = {
            "name": "test_shop_discount",
            "description": "some description",
            "discount_amount": 99,
            "discount_amount_type": 1,
            "start_date": self.date_now,
            "end_date": self.nex_date,
            "active": True,
        }

        categories = [self.categories.first()]
        products = [self.products.first()]
        form_data["products"] = products
        form_data["categories"] = categories
        form = self.shop_discount_form(form_data)

        if form.is_valid():
            discount = form.save(commit=False)
            discount.save()
            discount.products.set(products)
            discount.categories.set(categories)
            self.assertTrue(discount in ShopItemDiscount.objects.all())

    def test_create_cart_item_discount_success(self):
        """Создание записи скидки для товаров в корзине в таблицу через форму"""

        form_data = {
            "name": "test_shop_discount",
            "description": "some_description",
            "discount_amount": 99,
            "discount_amount_type": 1,
            "start_date": self.date_now,
            "end_date": self.nex_date,
            "active": True,
            "total_price_of_cart": 500,
            "amount_product_in_cart": 2,
        }
        products = [self.products.first()]
        categorise = [self.categories.last()]

        form = self.cart_discount_form(form_data)
        if form.is_valid():
            discount = form.save(commit=False)
            discount.save()
            discount.products.set(products)
            discount.categories.set(categorise)
            self.assertTrue(discount in CartItemDiscount.objects.all())
            self.assertEqual(discount.discount_amount, form_data["discount_amount"])

        else:
            raise ValidationError(form.errors)

    def test_create_shop_discount_error(self):
        """Проверка вывода ошибок при создании записи скидки для товаров в магазине"""
        incorrect_form_data = {
            "name": "test_shop_discount",
            "discount_amount": 100,
            "discount_amount_type": 1,
            "start_date": self.nex_date,
            "end_date": self.date_now,
            "active": True,
        }

        form = ShopDiscountCreationForm(incorrect_form_data)
        self.assertFormError(form, None, _("Заполните хотя бы одно поле для категории или товаров"))
        self.assertFormError(
            form,
            "end_date",
            _("Дата окончания действия скидки должна быть больше даты начала действия скидки"),
        )
        self.assertFormError(form, "discount_amount", _("Скидка в % не должна превышать 99 %"))

    def test_create_cart_discount_with_error(self):
        """Проверка вывода ошибок при создании записи скидки для товаров в корзине"""

        incorrect_form_data = {
            "name": "test_shop_discount",
            "discount_amount": 100,
            "discount_amount_type": 1,
            "start_date": self.nex_date,
            "end_date": self.date_now,
            "active": True,
        }

        form = self.cart_discount_form(incorrect_form_data)
        self.assertFormError(form, None, _("Заполните хотя бы одно условие для получения скидки"))
        self.assertFormError(
            form,
            "end_date",
            _("Дата окончания действия скидки должна быть больше даты начала действия скидки"),
        )
        self.assertFormError(form, "discount_amount", _("Скидка в % не должна превышать 99 %"))

        incorrect_form_data = {
            "name": "test_shop_discount",
            "discount_amount": 99,
            "discount_amount_type": 1,
            "start_date": self.date_now,
            "end_date": self.nex_date,
            "active": True,
            "categories": [self.categories.first()],
            "total_price_of_cart": 100,
            "amount_product_in_cart": 5,
        }

        form = CartDiscountCreationForm(incorrect_form_data)
        self.assertFormError(
            form,
            "products",
            _("При выборе категории поле товары должно быть заполнено"),
        )

    def test_discount_service(self):
        """Проверка работы сервиса обработки скидок"""

        request_mock = MagicMock()
        cart_mock = MagicMock(spec=Cart, request=request_mock)

        product1 = Product.objects.get(id=1)
        product2 = Product.objects.get(id=2)

        cart_mock.get_products.return_value = {
            product1: {"pcs": 1, "unit_price": 200},
            product2: {"pcs": 1, "unit_price": 200},
        }

        cart_mock.get_total_price.return_value = 400
        cart_mock.get_products_quantity.return_value = 2

        discounts = DiscountService(cart_mock)
        products_with_discount = discounts.get_product_with_new_price
        total_cart_price = discounts.get_total_price_with_discount
        self.assertEqual(products_with_discount, {product1: 50, product2: 50})
        self.assertEqual(total_cart_price, 100)

        cart_mock.get_products.return_value = {
            product1: {"pcs": 1, "unit_price": 100},
            product2: {"pcs": 1, "unit_price": 100},
        }

        cart_mock.get_total_price.return_value = 200
        cart_mock.get_products_quantity.return_value = 2
        discounts = DiscountService(cart_mock)
        products_with_discount = discounts.get_product_with_new_price
        total_cart_price = discounts.get_total_price_with_discount
        self.assertEqual(products_with_discount, {product1: 1, product2: 1})
        self.assertEqual(total_cart_price, 2)

from django.test import TestCase

from cart.models import Cart, CartItem
from users.models import CustomUser
from shops.models import Shop, Offer
from products.models import Product


class CartModelTest(TestCase):
    """Класс тестирования корзины"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = CustomUser.objects.create(username="user_test", password="123")
        cls.cart = Cart.objects.create(user=cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        CartModelTest.cart.delete()
        CartModelTest.user.delete()

    def test_verbose_name(self):
        cart = CartModelTest.cart
        verbose_name = {
            "user": "пользователь",
            "offer": "предложение",
        }
        for field, expected_value in verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(cart._meta.get_field(field).verbose_name, expected_value)


class CartItemModelTest(TestCase):
    """Класс тестирования элемента корзины"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = CustomUser.objects.create(username="user_test", password="123")
        cls.cart = Cart.objects.create(user=cls.user)
        cls.shop = Shop.objects.create(name="test_shop", user=cls.user)
        cls.product = Product.objects.create(name="test_product")
        cls.offer = Offer.objects.create(shop=cls.shop, product=cls.product, price=100)
        cls.cart_item = CartItem.objects.create(cart=cls.cart, offer=cls.offer, quantity=100)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        CartItemModelTest.cart_item.delete()
        CartItemModelTest.offer.delete()
        CartItemModelTest.product.delete()
        CartItemModelTest.shop.delete()
        CartItemModelTest.cart.delete()
        CartItemModelTest.user.delete()

    def test_verbose_name(self):
        cart_item = CartItemModelTest.cart_item
        verbose_name = {
            "cart": "корзина клиента",
            "offer": "товар магазина",
            "quantity": "количество товара в корзине",
        }
        for field, expected_value in verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(cart_item._meta.get_field(field).verbose_name, expected_value)

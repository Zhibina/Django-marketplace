import datetime
import json

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from shops.models import Offer
from .models import Cart as CartModel, CartItem


class Cart(object):
    """
    Класс корзины
    """

    def __init__(self, request):
        # initialization customer cart
        self.value = request.POST.get("value_amount")
        self.session = request.session
        self.user = request.user
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def __iter__(self):
        cart = self.cart_to_json(self.cart)
        for item in cart:
            yield item

    @staticmethod
    def cart_to_json(cart):
        """Возвращаем корзину из сессии в формате json"""
        cart_json = []
        for key, value in cart.items():
            try:
                offer = Offer.objects.get(id=key)
                cart_json.append(
                    {
                        "offer": offer,
                        "quantity": cart[key]["quantity"],
                        "created_at": cart[key]["created_at"],
                    }
                )
            except ObjectDoesNotExist:
                cart_json = []
        return cart_json

    def save(self):
        """Сохраняем корзину в сессии"""
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def save_to_db(self):
        """
        Если пользователь аутентифицирован, то сохраняем данные корзины в бд
        """
        if self.user.is_authenticated:
            try:
                cart_in_db = CartModel.objects.get(user=self.user)
            except ObjectDoesNotExist:
                cart_in_db = CartModel.objects.create(user=self.user)
            cart_in_session = self.cart_to_json(self.cart)
            for item_in_db in CartItem.objects.filter(cart=cart_in_db):
                if not any(item_in_db == item_session for item_session in cart_in_session):
                    item_in_db.delete()
            for session_item in cart_in_session:
                if CartItem.objects.filter(cart=cart_in_db).filter(offer=session_item["offer"].id).exists():
                    cart_item = CartItem.objects.filter(cart=cart_in_db).get(offer=session_item["offer"])
                    cart_item.quantity = session_item["quantity"]
                    cart_item.save()
                else:
                    cart_item = CartItem(
                        cart=cart_in_db,
                        offer=session_item["offer"],
                        quantity=session_item["quantity"],
                        created_at=session_item["created_at"],
                    )
                    cart_item.save()

    def save_to_session(self):
        """Сохраняем корзину из бд в сессиею"""
        cart_in_db = CartModel.objects.filter(user=self.user).first()
        if cart_in_db:
            cart_items = CartItem.objects.filter(cart=cart_in_db)
            for item_in_db in cart_items:
                self.cart[item_in_db.offer.id] = {
                    "quantity": item_in_db.quantity,
                    "created_at": json.dumps(item_in_db.created_at, default=str),
                }
            self.save()

    def add_to_cart(self, offer: Offer):
        """
        Записываем товар, его количество и дату добавления в сессию
        :param offer: Offer
        :param quantity: int
        """
        offer_id = str(offer.id)
        if offer_id in self.cart:
            self.cart_quantity_change(offer)
        else:
            self.cart[offer.id] = {
                "quantity": int(self.value),
                "created_at": json.dumps(datetime.datetime.now(), default=str),
            }
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True
        self.save_to_db()

    def delete_from_cart(self, offer: Offer):
        """
        Удаляем предложение из корзины
        :param offer: Offer
        """
        offer_id = str(offer.id)
        self.cart.pop(offer_id)
        self.session.modified = True
        self.save_to_db()

    def cart_quantity_change(self, offer: Offer):
        """ "Изменение товара в корзине, если товара меньше 0 удаляем товар из корзины"""
        offer_id = str(offer.id)
        if self.value == "+":
            self.cart[offer_id]["quantity"] += 1
        if self.value == "-":
            self.cart[offer_id]["quantity"] -= 1
        if self.value.isnumeric():
            self.cart[offer_id]["quantity"] += int(self.value)
        if self.cart[offer_id]["quantity"] == 0:
            self.cart.pop(offer_id)
            self.session.modified = True
        self.save_to_db()

    def get_products(self):
        """
        Возвращаем словарь с ключом Product значением словарь со значениями количество товара и цена товара
        :return: dict
        """
        cart = self.cart_to_json(self.cart)
        products = {
            item["offer"].product: {
                "pcs": item["quantity"],
                "unit_price": item["offer"].price,
            }
            for item in cart
        }
        return products

    def get_total_price(self):
        """
        Возвращаем общую цену товаров в корзине
        :return: decimal
        """

        json_cart = self.cart_to_json(self.cart)
        total_price = sum([item["offer"].price * item["quantity"] for item in json_cart])
        return total_price

    def get_products_quantity(self):
        """
        Возвращаем общую цену товаров в корзине
        :return: decimal
        """
        json_cart = self.cart_to_json(self.cart)
        products_quantity = sum([item["quantity"] for item in json_cart])
        return products_quantity

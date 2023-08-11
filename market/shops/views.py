import requests
from random import randrange
from django.shortcuts import render, redirect, reverse  # noqa F401
from django.conf import settings
from django.views.generic import TemplateView, View
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.decorators import api_view
from rest_framework.response import Response

from catalog.models import Catalog  # noqa F401
from products.models import Product
from users.views import MyLoginView
from shops.models import Shop, Order, OrderOffer, PaymentQueue
from shops.forms import OderLoginUserForm, PaymentForm
from shops.services.payment import update_order_status
from shops.services import banner
from shops.services.catalog import get_featured_categories
from shops.services.compare import (
    compare_list_check,
    splitting_into_groups_by_category,
    comparison_lists_and_properties,
)
from shops.services.is_member_of_group import is_member_of_group
from shops.services.get_paginator import get_paginator
from shops.services.order import save_order_model
from shops.services.order import pryce_delivery
from shops.services.limited_products import (
    get_random_limited_edition_product,
    get_top_products,
    get_limited_edition,
)
# from .services.limited_products import time_left  # пока не может использоваться из-за celery
from site_settings.models import SiteSettings

SRC_ORDER_STATUS_PK = 5
DST_ORDER_STATUS_PK = 4


def home(request):
    """Главная страница"""
    if request.method == "GET":
        site_settings = SiteSettings.load()
        page_number = request.GET.get('page')
        products = get_paginator(Product.objects.all()[:site_settings.top_elements_count], page_number)
        featured_categories = get_featured_categories()
        random_banners = banner.banner()
        top_products = get_top_products()
        # time_and_products = time_left()  # пока не может использоваться из-за celery
        # update_time = time_and_products['time_left']  # пока не может использоваться из-за celery
        # limited_products = time_and_products['limited_products']  # пока не может использоваться из-за celery
        limited_product = get_random_limited_edition_product()
        limited_edition = get_limited_edition().exclude(id=limited_product.id)[:site_settings.limited_edition_count]
        context = {
            "products": products,
            "featured_categories": featured_categories,
            "random_banners": random_banners,
            # 'update_time': update_time,  # пока не может использоваться из-за celery
            "limited_product": limited_product,
            "top_products": top_products,
            "limited_edition": limited_edition,
        }
        return render(request, "market/index.jinja2", context=context)


class BaseView(TemplateView):
    """Базовое представление страницы"""

    template_name = "market/base.jinja2"


@user_passes_test(is_member_of_group("Sellers"), login_url=reverse_lazy("account"))
def seller_detail(request):
    """Детальная страница продавца"""
    if request.method == "GET":
        shop = Shop.objects.filter(user=request.user.id)
        context = {
            "shop": shop,
        }
        return render(request, "market/shops/seller_detail.jinja2", context)


class ComparePageView(View):
    """Страница сравнения"""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Отображение страницы сравнения"""
        comp_list = self.request.session.get("comp_list", [])
        if comp_list and len(comp_list) > 1:
            category_offer_dict, category_count_product = splitting_into_groups_by_category(comp_list)
            list_compare, list_property = comparison_lists_and_properties(list(category_offer_dict.values())[0])
            context = {
                "category_offer_dict": category_count_product,
                "list_compare": list_compare,
                "list_property": list_property,
            }
            return render(request, "market/shops/comparison.jinja2", context=context)
        return render(
            request, "market/shops/comparison.jinja2", context={"text": "Не достаточно данных для сравнения."}
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        """Переключение категории сравнения и удаление из списка сравнений"""
        delete_id = self.request.POST.get("delete_id")
        if delete_id:
            compare_list_check(request.session, int(delete_id))
        comp_list = request.session.get("comp_list", [])
        if len(comp_list) > 1:
            category_name = self.request.POST.get("category")
            category_offer_dict, category_count_product = splitting_into_groups_by_category(comp_list)
            if category_name not in category_offer_dict:
                category_name = next(iter(category_offer_dict))
            list_compare, list_property = comparison_lists_and_properties(category_offer_dict[category_name])
            context = {
                "category_offer_dict": category_count_product,
                "list_compare": list_compare,
                "list_property": list_property,
            }
            return render(request, "market/shops/comparison.jinja2", context=context)

        return render(
            request, "market/shops/comparison.jinja2", context={"text": "Не достаточно данных для сравнения."}
        )


class CreateOrderView(TemplateView):
    """Оформление заказа"""

    def get(self, request, *args, **kwargs) -> HttpResponse:
        """Оформления заказа если корзина не пуста и пользователь залогинен"""
        cart_list = None
        if self.request.user.is_authenticated:
            cart_list = pryce_delivery(self.request.user)
            if not cart_list:
                return redirect("catalog:show_product")
        context = {
            "form_log": OderLoginUserForm(),
            "cart_list": cart_list,
        }
        return render(request, "market/order/order.jinja2", context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Аутентификация пользователя если незалогиненный.
        Сохранение заказа и истории изменения статуса
        """
        if not request.user.is_authenticated:
            form_log = OderLoginUserForm(self.request.POST)
            if form_log.is_valid():
                user = authenticate(email=form_log.cleaned_data["email"], password=form_log.cleaned_data["password"])
                if user:
                    login(self.request, user)
                    return redirect("order")
            else:
                return render(
                    self.request,
                    "market/order/order.jinja2",
                    context={
                        "text": "Неправильный ввод эмейла или пароля",
                        "user": self.request.user,
                    },
                )
        new_order_pk = save_order_model(self.request.user, self.request.POST, request.session)
        return redirect("payment", pk=new_order_pk)


class OrderLoginView(MyLoginView):
    """Вход пользователя"""

    next_page = reverse_lazy("order")


class HistoryOrderView(LoginRequiredMixin, View):
    """Страница история заказов"""

    login_url = reverse_lazy("users:users_login")

    def get(self, request: HttpRequest) -> HttpResponse:
        """Обработка GET запроса стр. истории заказов"""
        context = {
            "orders": Order.objects.filter(custom_user_id=self.request.user)
            .prefetch_related("status")
            .order_by("-data")
        }
        return render(request, "market/order/historyorder.jinja2", context=context)


class OrderDetailsView(LoginRequiredMixin, View):
    """Отображение деталей заказа"""

    login_url = reverse_lazy("users:users_login")

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Обработка GET запроса стр. детали заказа"""
        query = Order.objects.select_related("custom_user").get(id=pk)

        if self.request.user != query.custom_user:
            return HttpResponse("<h1>HTTP 403 Forbidden</h1>")
        context = {
            "order": query,
            "order_offers": OrderOffer.objects.filter(order_id=pk).prefetch_related("offer__product"),
        }
        return render(request, "market/order/oneorder.jinja2", context=context)


@api_view(["POST"])
def process_payment(request):
    """метод API для обработки запросов оплаты"""
    order_number = request.data["order_number"]
    card_number = request.data["card_number"]

    order = Order.objects.get(id=order_number)

    # Добавление заказа в очередь оплаты
    queue_job = PaymentQueue(order=order, card_number=card_number)
    queue_job.save()

    return Response({"message": "Payment request added to the queue"})


class PaymentView(LoginRequiredMixin, View):
    """Страница оплаты"""
    login_url = reverse_lazy("users:users_login")

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Выводит два варианта стр. с генератором номера карты и с полем ввода самостоятельно"""
        query_order = Order.objects.get(pk=pk)
        if query_order.pay == "SOMEONE":
            if self.request.GET.get("flag"):
                random_cart = randrange(10000000, 99999992, 2)
                context = {
                    "form": PaymentForm(initial={"card_number": random_cart}),
                    "pay": "ONLINE",
                    "order": query_order,
                }
                return render(request, "market/payment/payment.jinja2", context=context)

            context = {"form": PaymentForm(), "pay": query_order.pay, "order": query_order}
            return render(request, "market/payment/payment.jinja2", context=context)

        context = {"form": PaymentForm(), "pay": query_order.pay, "order": query_order}
        return render(request, "market/payment/payment.jinja2", context=context)

    def post(self, request: HttpRequest, pk, *args, **kwargs) -> HttpResponse:
        """Проверка валидности номера карты. Изменение статуса заказа. Отправка в очередь на оплату"""
        form = PaymentForm(request.POST)
        if form.is_valid():
            requests.post(settings.PAY_URL, data={"card_number": form.cleaned_data["card_number"], "order_number": pk})
            update_order_status(pk, SRC_ORDER_STATUS_PK, DST_ORDER_STATUS_PK)
            return redirect("catalog:show_product")

        query_order = Order.objects.get(pk=pk)
        context = {"form": form, "pay": query_order.pay, "order": query_order}
        return render(request, "market/payment/payment.jinja2", context=context)

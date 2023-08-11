from django.core.paginator import Paginator
from django.db.models import Q, Avg, Min
from django.http import HttpRequest

from catalog.forms import ProductFilterForm
from catalog.price_and_discounts import check_discount_price, min_price, max_price
from products.models import Product
from site_settings.models import SiteSettings
from shops.services.compare import compare_list_check


def get_paginator(request: HttpRequest or dict, products, forms) -> dict:
    """Представление пагинации 'Каталог продуктов' и сессия для сортировки"""
    if request.GET.get("sort"):
        request.session["sorted"] = request.GET.get("sort")
        sort = request.session["sorted"]
        products = sorted_products(sort, products)
    else:
        if "sorted" in request.session:
            sort_session = request.session["sorted"]
            products = sorted_products(sort_session, products)
    if request.POST.get("add_compare"):
        get = request.POST.get("add_compare")
        compare_list_check(request.session, get)
    pagination_value = SiteSettings.objects.values_list('pagination_size', flat=True).first()
    paginator = Paginator(products, pagination_value)
    check_discount_price()
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    context = {
        "page_obj": page_obj,
        "form": forms,
    }
    return context


def sorted_products(sort: str, product) -> list or dict:
    """Сортировка по критериям"""
    if sort in "offers__price":
        product = (
            product.prefetch_related("offers")
            .annotate(average_stars=Avg("offers__discount_price"))
            .order_by("average_stars")
        )
        return product
    elif sort in "-offers__date_of_creation":
        product = product.prefetch_related("offers").annotate(date=Min("offers__date_of_creation")).order_by("-date")
        return product
    elif sort in ("sorting.get_count_history()", "sorting.get_count_reviews()"):
        product = {
            sorting: sorting.get_count_reviews()
            if sort == "sorting.get_count_reviews()"
            else sorting.get_count_history()
            for sorting in product
        }
        product = sorted(product.items(), key=lambda key: key[1])[::-1]
        product = [value for value, key in product]
        return product
    else:
        return product


def filter_search(session: dict, products) -> dict:
    """Фильтрация продуктов"""
    prices = session["price"].split(";")
    sessions = {value: key for value, key in session.items() if (session[value] and value != "price")}
    product_search = (
        products.prefetch_related("offers")
        .annotate(discount=Avg("offers__discount_price"))
        .filter(
            (
                Q(name__icontains="" if sessions.get("name") is None else sessions["name"])
                & Q(discount__range=(prices[0], prices[1]))
            )
        )
    )

    if sessions.get("in_stock"):
        product_search = (
            products.prefetch_related("offers")
            .annotate(discount=Avg("offers__discount_price"))
            .filter(
                (
                    Q(name__icontains="" if sessions.get("name") is None else sessions["name"])
                    & Q(discount__range=(prices[0], prices[1]))
                )
                & Q(offers__product_in_stock=None if sessions.get("in_stock") is None else sessions["in_stock"])
            )
        )

    if sessions.get("free_delivery"):
        product_search = (
            products.prefetch_related("offers")
            .annotate(discount=Avg("offers__discount_price"))
            .filter(
                (
                    Q(name__icontains="" if sessions.get("name") is None else sessions["name"])
                    & Q(discount__range=(prices[0], prices[1]))
                )
                & Q(offers__free_shipping=None if sessions.get("free_delivery") is None else sessions["free_delivery"])
            )
        )
    if sessions.get("in_stock") and sessions.get("free_delivery"):
        product_search = (
            products.prefetch_related("offers")
            .annotate(discount=Avg("offers__discount_price"))
            .filter(
                (
                    Q(name__icontains="" if sessions.get("name") is None else sessions["name"])
                    & Q(discount__range=(prices[0], prices[1]))
                )
                & Q(offers__free_shipping=None if sessions.get("free_delivery") is None else sessions["free_delivery"])
                & Q(offers__product_in_stock=None if sessions.get("in_stock") is None else sessions["in_stock"])
            )
        )
    return product_search.distinct()


def session_verification(session: dict) -> dict or None:
    """Проверка сессий"""
    if "filter" in session:
        sessions = session["filter"]
        prices = sessions["price"].split(";")
        form = ProductFilterForm(session["filter"])
        if "search" in session:
            search = session["search"]
            products = Product.objects.filter((Q(name__icontains=search)))
        else:
            products = Product.objects.all()
        if form.is_valid():
            form.fields["price"].widget.attrs.update(
                {
                    "data-from": prices[0],
                    "data-to": prices[1],
                    "data-min": str(min_price()),
                    "data-max": str(max_price()),
                }
            )
            products = filter_search(sessions, products)
            return products, form
    else:
        return False

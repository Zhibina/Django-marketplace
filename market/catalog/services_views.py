from django.db.models import Q
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render

from catalog.forms import ProductFilterForm
from catalog.price_and_discounts import (
    min_price,
    max_price,
    check_discount_price,
    min_price_for_category,
    max_price_for_category,
)
from catalog.services import filter_search, get_paginator, session_verification
from products.models import Product


class CatalogMixin:
    """Представление 'Каталог продуктов'"""

    def get(self, request: HttpRequest and dict) -> HttpResponse:
        sessions = request.session
        if session_verification(sessions):
            products, form = session_verification(sessions)
        else:
            form = ProductFilterForm()
            form.fields["price"].widget.attrs.update(
                {
                    "data-from": str(min_price() + (min_price() * 30 / 100)),
                    "data-to": str(max_price() - (max_price() * 20 / 100)),
                    "data-min": str(min_price()),
                    "data-max": str(max_price()),
                }
            )
            if request.session.get("search"):
                products = Product.objects.filter((Q(name__icontains=sessions["search"])))
            else:
                products = Product.objects.all().prefetch_related("offers")
        context = get_paginator(request, products, form)
        return render(request, "market/catalog/catalog.jinja2", context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        if request.session.get("search"):
            product = Product.objects.filter((Q(name__icontains=request.session.get("search"))))
        else:
            product = Product.objects.all().prefetch_related("offers")
        form = ProductFilterForm(request.POST)
        if form.is_valid():
            prices = form.cleaned_data["price"].split(";")
            check_discount_price()
            form.fields["price"].widget.attrs.update(
                {
                    "data-from": prices[0],
                    "data-to": prices[1],
                    "data-min": str(min_price()),
                    "data-max": str(max_price()),
                }
            )
            request.session.set_expiry(180)
            request.session["filter"] = form.cleaned_data
            session = request.session["filter"]
            product = filter_search(session, product)
        else:
            form = ProductFilterForm()
        context = get_paginator(request, product, form)
        return render(request, "market/catalog/catalog.jinja2", context=context)


class CatalogCategoryMixin:
    """Представление 'Каталог продуктов по категориям'"""

    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        if request.session.get("path") == request.path:
            if "filter" in request.session:
                sessions = request.session["filter"]
                prices = sessions["price"].split(";")
                products = Product.objects.filter(category__slug=slug)
                form = ProductFilterForm(request.session["filter"])
                if form.is_valid():
                    form.fields["price"].widget.attrs.update(
                        {
                            "data-from": prices[0],
                            "data-to": prices[1],
                            "data-min": str(min_price_for_category(slug)),
                            "data-max": str(max_price_for_category(slug)),
                        }
                    )
                    products = filter_search(sessions, products)
        else:
            form = ProductFilterForm()
            form.fields["price"].widget.attrs.update(
                {
                    "data-from": str(min_price_for_category(slug)),
                    "data-to": str(max_price_for_category(slug)),
                    "data-min": str(min_price_for_category(slug)),
                    "data-max": str(max_price_for_category(slug)),
                }
            )
            products = Product.objects.filter(category__slug=slug)
        context = get_paginator(request, products, form)
        return render(request, "market/catalog/catalog.jinja2", context=context)

    def post(self, request: HttpRequest, slug: str) -> HttpResponse:
        product = Product.objects.filter(category__slug=slug)
        form = ProductFilterForm(request.POST)
        if form.is_valid():
            prices = form.cleaned_data["price"].split(";")
            check_discount_price()
            form.fields["price"].widget.attrs.update(
                {
                    "data-from": prices[0],
                    "data-to": prices[1],
                    "data-min": str(min_price_for_category(slug)),
                    "data-max": str(max_price_for_category(slug)),
                }
            )
            request.session.set_expiry(60 * 20)
            request.session["filter"] = form.cleaned_data
            request.session["path"] = request.path
            session = request.session["filter"]
            product = filter_search(session, product)
        else:
            form = ProductFilterForm()
        context = get_paginator(request, product, form)
        return render(request, "market/catalog/catalog.jinja2", context=context)

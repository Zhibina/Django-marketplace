from django.db.models import Min, Max, Avg
from products.models import Product


def min_price() -> int:
    products = Product.objects.all()
    price = products.annotate(price_min_discount=Avg("offers__discount_price")).aggregate(Min("price_min_discount"))
    return round(price["price_min_discount__min"] or 0)


def max_price() -> int:
    products = Product.objects.all()
    price = products.annotate(price_max_discount=Avg("offers__discount_price")).aggregate(Max("price_max_discount"))
    return round(price["price_max_discount__max"] or 0)


def min_price_for_category(slug: str) -> int:
    products = Product.objects.filter(category__slug=slug)
    price = products.annotate(price_min_discount=Avg("offers__discount_price")).aggregate(Min("price_min_discount"))
    return round(price["price_min_discount__min"] or 0)


def max_price_for_category(slug: str) -> int:
    products = Product.objects.filter(category__slug=slug)
    price = products.annotate(price_max_discount=Avg("offers__discount_price")).aggregate(Max("price_max_discount"))
    return round(price["price_max_discount__max"] or 0)


def check_discount_price():
    """Обновление цены со скидкой"""
    products = Product.objects.all()
    for product in products:
        for ii in product.offers.only("discount_price"):
            ii.discount_price = ii.price_with_discount
            ii.save()

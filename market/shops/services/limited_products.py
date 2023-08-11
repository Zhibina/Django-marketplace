import random
from collections import Counter
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from products.models import Product, Browsing_history
from site_settings.models import SiteSettings
from ..tasks import update_product_of_the_day


def get_limited_edition():
    """возвращает продукты с галочкой 'ограниченные предложения'"""
    edition = Product.objects.filter(limited_edition=True)
    if edition:
        return edition
    return None


def get_top_products():
    """Представление топ-продуктов (первые 8)"""
    site_settings = SiteSettings.load()
    products_history = Browsing_history.objects.all()
    products = sorted(list(Counter(Product.objects.filter(products__in=products_history)).
                           items()), key=lambda key: key[1])[:-site_settings.hot_deals_slider-1:-1]
    products = [value for value, key in products]
    if products:
        return products
    return None


def get_random_limited_edition_product():
    """Получает список всех товаров с флагом limited_edition"""
    products = Product.objects.filter(limited_edition=True)
    if products:
        product = random.choice(products)
        return product
    return None


def time_left():
    """возвращает список товаров, который получается из кэша или из базы данных, если кэш пуст
    и объект timedelta, который показывает, сколько времени осталось до истечения срока действия товаров
     с ограниченным тиражом."""
    limited_products = cache.get("limited_products")
    if not limited_products:
        update_product_of_the_day.delay()
        limited_products = Product.objects.none()
    now = timezone.now()
    expires_at = cache.get("limited_products.cache_timeout")
    if not expires_at:
        expires_at = now + timedelta(hours=23)  # Начальное значение
    time_l = (expires_at - now).total_seconds()
    time_l = max(time_l, 0)  # Удаляем отрицательное значение
    time_l = timedelta(seconds=time_l)

    return {
        "limited_products": limited_products,
        "time_left": time_l,
    }


def get_offer_of_the_day_cache_key():
    """Получает уникальный ключ для кеширования предложения дня"""
    key = make_template_fragment_key("offer_of_the_day")
    return key


def invalidate_offer_of_the_day_cache():
    """Сбрасывает кеш предложения дня"""
    key = get_offer_of_the_day_cache_key()
    cache.delete(key)

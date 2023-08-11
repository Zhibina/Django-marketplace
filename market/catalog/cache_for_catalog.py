from django.conf import settings
from django.core.cache import cache


def clear_cache_catalog():
    """Очищает весь кэш Catalog"""
    key_prefix = "catalog"
    select_keys = cache.keys(
        f"views.decorators.cache.cache_header.{key_prefix}.*.{settings.LANGUAGE_CODE}.{settings.TIME_ZONE}"
    )
    select_keys_get = cache.keys(
        f"views.decorators.cache.cache_page.{key_prefix}.GET.*.{settings.LANGUAGE_CODE}.{settings.TIME_ZONE}"
    )
    select_cache = cache.get_many(select_keys)
    select_cache_get = cache.get_many(select_keys_get)
    cache.delete_many(select_cache)
    cache.delete_many(select_cache_get)


def clear_cache_category():
    """Сброс кэша для категорий"""
    select_keys = cache.keys("template.cache.<QuerySet *.*")
    select_cache_get = cache.get_many(select_keys)
    cache.delete_many(select_cache_get)

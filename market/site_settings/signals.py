from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings
from market.site_settings.models import SiteSettings


@receiver(post_save, sender=SiteSettings)
def clear_home_cache(sender, instance, **kwargs):
    key_prefix = "home"
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

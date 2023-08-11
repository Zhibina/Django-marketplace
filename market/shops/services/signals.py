from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from market.products.models import Product
from .limited_products import invalidate_offer_of_the_day_cache


@receiver(post_save, sender=Product)
def product_saved(sender, instance, **kwargs):
    """Сбрасывает кеш предложения дня при сохранении товара"""
    invalidate_offer_of_the_day_cache()


@receiver(post_delete, sender=Product)
def product_deleted(sender, instance, **kwargs):
    """Сбрасывает кеш предложения дня при удалении товара"""
    invalidate_offer_of_the_day_cache()

from django.contrib import admin

from .models import CartItem, Cart


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Отображение модели корзины и количества продуктов в ней
    """

    list_display = ["id", "user"]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Отображение модели корзины и количества продуктов в ней
    """

    list_display = ["id", "cart", "offer", "quantity", "created_at"]

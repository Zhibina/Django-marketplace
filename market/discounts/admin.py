from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from discounts.models import ShopItemDiscount, CartItemDiscount
from discounts.forms import ShopDiscountCreationForm, CartDiscountCreationForm
from discounts.services.admin_service import formatted_last_time_service


@admin.register(ShopItemDiscount)
class ShopDiscountAdmin(admin.ModelAdmin):
    """Класс для отображения скидок на товары в магазине"""

    form = ShopDiscountCreationForm
    list_display = ("name", "active", "formatted_last_time")
    search_fields = ["name"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "discount_amount",
                    "discount_amount_type",
                    "start_date",
                    "end_date",
                )
            },
        ),
        (
            _("Скидка на группу товаров"),
            {"fields": ("products", "categories")},
        ),
        (_("Активировать скидку"), {"fields": ("active",)}),
    )

    def formatted_last_time(self, obj):
        """Функция для отображения окончания действия скидки"""
        return formatted_last_time_service(obj)

    formatted_last_time.short_description = _("Время до окончания действия скидки")


@admin.register(CartItemDiscount)
class CartDiscountAdmin(admin.ModelAdmin):
    """Класс для отображения скидок на товары в корзине"""

    form = CartDiscountCreationForm
    list_display = ("name", "active", "formatted_last_time")
    search_fields = ["name"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "discount_amount",
                    "discount_amount_type",
                    "start_date",
                    "end_date",
                )
            },
        ),
        (
            _("Скидка на группу товаров"),
            {"fields": ("products", "categories")},
        ),
        (
            _("Дополнительные параметры"),
            {
                "fields": (
                    "total_price_of_cart",
                    "amount_product_in_cart",
                )
            },
        ),
        (_("Активировать скидку"), {"fields": ("active",)}),
    )

    def formatted_last_time(self, obj):
        """Функция для отображения окончания действия скидки"""
        return formatted_last_time_service(obj)

    formatted_last_time.short_description = _("Время до окончания действия скидки")

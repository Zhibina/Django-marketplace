from collections import Counter
from django.contrib import admin  # noqa F401
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from catalog.cache_for_catalog import clear_cache_catalog
from .models import Shop, Offer, Banner, Order, OrderStatus, OrderStatusChange


class ShopProductForm(BaseInlineFormSet):
    """Валидация на добавление более 2-х продуктов с одиноковым id.
    После валидности, кэш Catalog очищается"""

    def clean(self):
        super(ShopProductForm, self).clean()
        product = list()
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get("DELETE"):
                product.append(form.cleaned_data.get("product"))
        data = Counter(product)
        for ii in data.values():
            if ii > 1:
                raise ValidationError(f"Ошибка. Продукт{product[-1:]} не может повторяться")
            else:
                clear_cache_catalog()


class ShopProductInline(admin.TabularInline):
    model = Shop.products.through
    formset = ShopProductForm
    exclude = ("discount_price",)


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    inlines = [
        ShopProductInline,
    ]
    list_display = (
        "name",
        "user",
        "phone_number",
        "email",
    )


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        "shop",
        "product",
        "price",
    )
    exclude = ("discount_price",)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    """вывод и фильтрация полей баннера в административной панели"""

    list_display = ("title", "description", "image", "active")
    list_filter = ("active",)
    search_fields = ("title",)


class OrderOfferAdminInline(admin.TabularInline):
    """Вставка модели Order"""

    model = Order.offer.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Отображение заказов в интерфейсе администратора"""

    inlines = [
        OrderOfferAdminInline,
    ]
    list_display = (
        "id",
        "custom_user",
        "status",
        "data",
        "delivery",
        "city",
        "address",
    )


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    """Отображение статусов заказав в интерфейсе администратора"""

    list_display = (
        "sort_index",
        "name",
    )


@admin.register(OrderStatusChange)
class OrderStatusChangeAdmin(admin.ModelAdmin):
    """Отображение истории изменения статусов заказав в интерфейсе администратора"""

    list_display = (
        "id",
        "time",
        "src_status_id",
        "dst_status_id",
    )

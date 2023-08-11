from django.contrib import admin  # noqa F401
from .models import Product, ProductProperty, Property, ProductImage, Review
from django.utils.translation import gettext_lazy as _


class ProductProductImageInline(admin.TabularInline):
    model = ProductImage


class ProductPropertyInline(admin.TabularInline):
    model = Product.property.through


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Отображение модели продуктов в админ панели"""

    inlines = [
        ProductProductImageInline,
        ProductPropertyInline,
    ]
    list_display = "name", "preview", "rating_field", "reviews_field"

    def reviews_field(self, obj):
        reviews = obj.get_count_reviews()
        return reviews

    reviews_field.short_description = _("Количество отзывов")

    def rating_field(self, obj):
        rating = obj.get_average_rating()
        return round(rating, 2)

    rating_field.short_description = _("Рейтинг товара")


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """Отображение модели свойств в админ панели"""

    list_display = ("name",)


@admin.register(ProductProperty)
class ProductProperty(admin.ModelAdmin):
    """Отображение модели свойств продуктов в админ панели"""

    list_display = (
        "product",
        "property",
        "value",
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Отображение модели отзывов в админ панели"""

    list_display = "product", "user", "rating"
    search_fields = ["user"]

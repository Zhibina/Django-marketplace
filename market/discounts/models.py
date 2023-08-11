from datetime import timedelta

from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _

from catalog.price_and_discounts import check_discount_price


class StatusDiscount(models.IntegerChoices):
    """Класс для выбора вида скидки"""

    percentages = 1, _("проценты")
    amount = 2, _("сумма")


class Discount(models.Model):
    """Абстрактный класс для модели скидок"""

    class Meta:
        abstract = True

    name = models.CharField(max_length=50, null=False, blank=False, verbose_name=_("название скидки"))
    description = models.TextField(max_length=150, verbose_name=_("Описание скидки"))
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("размер скидки"),
        null=False,
        blank=False,
    )
    discount_amount_type = models.PositiveSmallIntegerField(choices=StatusDiscount.choices, null=False, blank=False)
    active = models.BooleanField(verbose_name=_("скидка активна"), null=False, blank=False)
    start_date = models.DateTimeField(null=False, blank=False, verbose_name=_("дата начала действия скидки"))
    end_date = models.DateTimeField(null=False, blank=False, verbose_name=_("дата окончания действия скидки"))

    products = models.ManyToManyField(
        "products.Product",
        blank=True,
        related_name="%(class)s",
        verbose_name=_("товары"),
    )
    categories = models.ManyToManyField(
        "catalog.Catalog",
        blank=True,
        related_name="%(class)s",
        verbose_name=_("категории товаров"),
    )

    def __str__(self):
        """Метод для отображения имени записи в таблице"""
        return f"id: {self.id} name: {self.name}"

    @property
    def last_discount_time(self):
        """Метод для времени до даты истечения скидки"""
        current_time = timezone.now()
        last_time = self.end_date - current_time
        if self.active:
            if last_time.total_seconds() <= 0:
                self.active = False
                self.save()
                last_time = timedelta(seconds=0)
        else:
            last_time = timedelta(seconds=0)

        return last_time

    def save(self, *args, **kwargs):
        self.active = self.last_discount_time.total_seconds() > 0
        check_discount_price()
        super().save(*args, **kwargs)


class ShopItemDiscount(Discount):
    """Модель скидок для товаров в магазине"""

    class Meta:
        verbose_name = _("скидка на товар в магазине")
        verbose_name_plural = _("скидки на товары в магазине")


class CartItemDiscount(Discount):
    """Модель скидок для товаров в корзине"""

    class Meta:
        verbose_name = _("скидка на товар в корзине")
        verbose_name_plural = _("скидки на товары в корзине")

    total_price_of_cart = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Минимальная цена товаров в корзине"),
        help_text=_("Скидка может быть установлена на стоимость товаров в корзине."),
    )

    amount_product_in_cart = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Минимальное количество товаров в корзине"),
        help_text=_("Скидка может быть установлена на количество товаров в корзине."),
    )

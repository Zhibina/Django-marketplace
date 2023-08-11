from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser as User


class Cart(models.Model):
    """
    Модель корзины покупателя
    """

    class Meta:
        verbose_name = _("корзина")
        verbose_name_plural = _("корзины")

    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="carts",
        verbose_name=_("пользователь"),
    )
    offer = models.ManyToManyField("shops.Offer", through="CartItem", verbose_name=_("предложение"))


class CartItem(models.Model):
    """
    Модель товар в корзине(предложение от магазина) и его количество
    """

    class Meta:
        verbose_name = _("товар в корзине")
        verbose_name_plural = _("товары в корзине")

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="offers",
        verbose_name=_("корзина клиента"),
    )
    offer = models.ForeignKey("shops.Offer", on_delete=models.CASCADE, verbose_name=_("товар магазина"))
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("количество товара в корзине"),
        default=1,
    )
    created_at = models.DateTimeField(auto_now_add=True)

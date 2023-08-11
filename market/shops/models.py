from django.core.validators import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser
from shops.services.offer_discount import OfferDiscount


class Shop(models.Model):
    """Магазин"""

    name = models.CharField(max_length=512, verbose_name=_("название"))
    products = models.ManyToManyField(
        "products.Product",
        through="Offer",
        related_name="shops",
        verbose_name=_("товары в магазине"),
    )
    user = models.OneToOneField("users.CustomUser", on_delete=models.CASCADE, verbose_name=_("пользователь"))
    phone_number = models.CharField(max_length=13, verbose_name=_("номер телефона"))
    email = models.EmailField(max_length=100, verbose_name=_("почта"))

    def __str__(self):
        return self.name


class Offer(models.Model):
    """Предложение магазина"""

    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT, related_name="offers")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("цена"))
    discount_price = models.DecimalField(max_digits=10, default=0, decimal_places=2, verbose_name=_("цена со скидкой"))
    product_in_stock = models.BooleanField(default=True, verbose_name=_("товар в наличии"))
    free_shipping = models.BooleanField(default=False, verbose_name=_("бесплатная доставка"))
    date_of_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"shop{self.shop.name}, product: {self.product.name}"

    @property
    def product_discount(self):
        """Вывод скидки на продукт"""
        discount = OfferDiscount(self)
        return discount()

    @property
    def price_with_discount(self):
        """Вывод цены продукта со скидкой"""
        price = self.price - self.product_discount
        if price <= 0:
            price = 1
        return price


class Banner(models.Model):
    """Модель баннеров"""

    class Meta:
        verbose_name = _("баннер")
        verbose_name_plural = _("баннеры")

    title = models.CharField(max_length=280, verbose_name=_("название баннера"))
    description = models.TextField(max_length=280, null=True, verbose_name=_("описание баннера"))
    image = models.ImageField(upload_to="media/banners/", verbose_name=_("изображение баннера"))

    active = models.BooleanField(default=True, verbose_name=_("статус активности баннера"))

    def __str__(self):
        return self.title


class OrderStatus(models.Model):
    """Модель статуса заказа"""

    class Meta:
        verbose_name = _("статус заказа")
        verbose_name_plural = _("статусы заказа")
        ordering = ["sort_index"]

    sort_index = models.SmallIntegerField(unique=True, verbose_name=_("порядковый индекс"))
    name = models.CharField(max_length=100, verbose_name=_("статус заказа"))

    def __str__(self):
        return self.name


class StatusDeliveryOrder(models.TextChoices):
    """Варианты выбор доставки"""

    ORDINARY = "ORDINARY", _("Обычная")
    EXPRESS = "EXPRESS", _("Экспрес")


class StatusPayOrder(models.TextChoices):
    """Варианты выбора способа оплаты"""

    ONLINE = "ONLINE", _("Онлайн")
    SOMEONE = "SOMEONE", _("Онлайн со случайного чужого счета")


class Order(models.Model):
    """Модель заказов"""

    class Meta:
        verbose_name = _("заказ")
        verbose_name_plural = _("заказы")

    custom_user = models.ForeignKey(
        CustomUser, on_delete=models.PROTECT, related_name="orders", verbose_name=_("пользователь")
    )
    offer = models.ManyToManyField(Offer, through="OrderOffer", related_name="orders", verbose_name=_("предложение"))
    status = models.ForeignKey(
        OrderStatus, on_delete=models.PROTECT, related_name="orders", default=1, verbose_name=_("статус")
    )
    data = models.DateTimeField(auto_now_add=True, verbose_name=_("дата создания"))
    delivery = models.CharField(
        max_length=8,
        choices=StatusDeliveryOrder.choices,
        verbose_name=_("доставка"),
        default=StatusDeliveryOrder.ORDINARY,
    )
    city = models.CharField(max_length=100, verbose_name=_("город"))
    address = models.CharField(max_length=200, verbose_name=_("адрес"))
    pay = models.CharField(
        max_length=8, choices=StatusPayOrder.choices, verbose_name=_("вид оплаты"), default=StatusPayOrder.ONLINE
    )
    total_cost = models.DecimalField(decimal_places=2, max_digits=10)


class OrderOffer(models.Model):
    """Промежуточная модель. Дополнительное поле количество товара"""

    class Meta:
        verbose_name = _("Товар")
        verbose_name_plural = _("Товары")

    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    offer = models.ForeignKey(Offer, on_delete=models.PROTECT, verbose_name=_("Товары"))
    count = models.PositiveSmallIntegerField(verbose_name=_("количество"))
    price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name=_("цена"))


class OrderStatusChange(models.Model):
    """Модель сохранения хронологии изменения статуса заказа"""

    class Meta:
        verbose_name = _("изменение статуса заказа")
        verbose_name_plural = _("изменение статусов заказов")
        ordering = ["-time"]

    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    time = models.DateTimeField(auto_now_add=True, verbose_name=_("время изменения"))
    src_status = models.ForeignKey(OrderStatus, related_name="orders_order_change_src", on_delete=models.PROTECT)
    dst_status = models.ForeignKey(OrderStatus, related_name="orders_order_change_dst", on_delete=models.PROTECT)


def validate_card_number(value):
    """Проверка валидности карты оплаты"""
    if 10000000 > value or value > 99999999 or value % 2 != 0:
        raise ValidationError(_(f"{value} номер должен быть четным от 1000 0000 до 9999 9999 включительно"))


class PaymentQueue(models.Model):
    """Модель для представления задания оплаты в очереди"""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name=_("заказ"))
    card_number = models.IntegerField(validators=[validate_card_number], verbose_name=_("номер карты"))

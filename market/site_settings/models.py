from django.db import models
from django.core.validators import MaxValueValidator
from django.utils.translation import gettext_lazy as _


class OneObjectModel(models.Model):
    """Модель, которая имеет один объект"""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(OneObjectModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()


class SiteSettings(OneObjectModel):
    """Модель настроек сайта, позволяет установить значение пагинации,
     количество банеров, горячих предложений, топ товаров, ограниченный тираж,
     количество просмотренных товаров, минимальная сумма заказа для бесплатной доставки,
     стандартная цена доставки и стоимость экспресс-доставки"""

    pagination_size = models.PositiveIntegerField(validators=[MaxValueValidator(8)], default=4,
                                                  verbose_name=_('размер пагинации, объектов'))
    banners_count = models.PositiveIntegerField(validators=[MaxValueValidator(3)], default=3,
                                                verbose_name=_('количество баннеров'))
    hot_deals_slider = models.PositiveIntegerField(validators=[MaxValueValidator(9)], default=9,
                                                   verbose_name=_('количество горячих предложений'))
    top_elements_count = models.PositiveIntegerField(validators=[MaxValueValidator(8)], default=8,
                                                     verbose_name=_('количество товаров в топе'))
    limited_edition_count = models.PositiveIntegerField(validators=[MaxValueValidator(16)], default=16,
                                                        verbose_name=_('количество ограниченного тиража'))
    maximum_number_of_viewed_products = models.PositiveIntegerField(validators=[MaxValueValidator(20)], default=10,
                                                                    verbose_name=_(
                                                                        'максимальное количество просмотренных товаров'
                                                                    ))
    free_shipping_min_order_amount = models.DecimalField(max_digits=6, decimal_places=2, default=2000.00,
                                                         verbose_name=_(
                                                             'минимальная сумма заказа для бесплатной доставки, $'))
    standard_shipping_price = models.DecimalField(max_digits=6, decimal_places=2, default=200.00,
                                                  verbose_name=_('стандартная цена доставки, $'))
    express_shipping_price = models.DecimalField(max_digits=6, decimal_places=2, default=500.00,
                                                 verbose_name=_('стоимость экспресс-доставки, $'))

    def __str__(self) -> str:
        return "Site settings"

    class Meta:
        verbose_name = _("настройка сайта")
        verbose_name_plural = _("настройки сайта")

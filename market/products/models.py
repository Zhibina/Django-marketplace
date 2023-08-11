from django.db import models
from django.utils.translation import gettext_lazy as _

from catalog.cache_for_catalog import clear_cache_catalog
from users.models import CustomUser as User
from django.db.models import Avg, ManyToManyField
from taggit.managers import TaggableManager


def product_preview_directory_path(instance: "Product", filename: str) -> str:
    """Генерирует путь к картинке"""

    return "products/product_{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


class Product(models.Model):
    """Продукт"""

    tags = TaggableManager()

    class Meta:
        verbose_name_plural = _("продукты")
        verbose_name = _("продукт")

    name = models.CharField(max_length=512, db_index=True, verbose_name=_("наименование"))
    limited_edition = models.BooleanField(default=False, verbose_name=_("ограниченный тираж"))
    index = models.PositiveIntegerField(default=0, verbose_name=_("индекс сортировки"))
    preview = models.ImageField(
        null=True,
        blank=True,
        upload_to=product_preview_directory_path,
        verbose_name=_("предварительный просмотр"),
    )
    property: ManyToManyField = models.ManyToManyField(
        "Property", through="ProductProperty", verbose_name=_("характеристики")
    )
    category = models.ForeignKey(
        "catalog.Catalog",
        on_delete=models.PROTECT,
        null=True,
        related_name="category",
        verbose_name=_("категория"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("описание"),
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Очистка кэша при добавлении или изменении продукта"""
        clear_cache_catalog()
        super().save(*args, **kwargs)

    def get_count_reviews(self) -> int:
        """Вывод количества отзывов о продукте"""
        return Review.objects.filter(product=self).count()

    def get_average_rating(self) -> float:
        """Вывод средней оценки продукта"""
        return Review.objects.filter(product=self).aggregate(Avg("rating")).get("rating__avg") or 0

    def get_count_history(self) -> int:
        """Подсчет просмотров истории продукта"""
        return Browsing_history.objects.filter(product=self).count()


class Property(models.Model):
    """Свойство продукта"""

    class Meta:
        verbose_name_plural = _("свойства")
        verbose_name = _("свойство")

    name = models.CharField(max_length=512, verbose_name=_("наименование"))

    def __str__(self):
        return self.name


class ProductProperty(models.Model):
    """Значение свойства продукта"""

    class Meta:
        verbose_name_plural = _("свойства продуктов")
        unique_together = (("product", "property"),)
        verbose_name = _("свойство продукта")

    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    property = models.ForeignKey(Property, on_delete=models.PROTECT, verbose_name=_("свойство"))
    value = models.CharField(max_length=128, verbose_name=_("значение"))


def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    """Генерирует путь к картинке"""

    return "products/product_{pk}/images/{filename}".format(pk=instance.product.pk, filename=filename)


class ProductImage(models.Model):
    class Meta:
        verbose_name_plural = _("изображение продукта")
        verbose_name = _("изображения продуктов")

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_images")
    image = models.ImageField(upload_to=product_images_directory_path, verbose_name=_("изображение"))
    description = models.CharField(max_length=200, null=False, blank=True, verbose_name=_("описание"))


class StatusReview(models.IntegerChoices):
    very_bad = 1, "1"
    bad = 2, "2"
    satisfactory = 3, "3"
    well = 4, "4"
    very_well = 5, "5"


class Review(models.Model):
    """Модель отзывов о товаре и его оценка"""

    class Meta:
        unique_together = ("user", "product")
        verbose_name = _("отзыв")
        verbose_name_plural = _("отзывы")

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name=_("покупатель"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("продукт"))
    # order = models.ForeignKey("Order", on_delete=models.DO_NOTHING, verbose_name=_("Заказ"))
    rating = models.PositiveSmallIntegerField(
        choices=StatusReview.choices,
        verbose_name=_("оценка"),
    )
    review_text = models.TextField(max_length=500, blank=False, null=True, verbose_name=_("текст отзыва"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user, self.product, self.rating}"

    @classmethod
    def get_review(cls, user_id=None, product_id=None):
        """Функция для получения отзывов"""
        reviews = Review.objects.select_related("user").select_related("product").order_by("created_at")
        if user_id is not None:
            reviews = reviews.filter(user=user_id)
        if product_id is not None:
            reviews = reviews.filter(product_id=product_id)

        return reviews


class Browsing_history(models.Model):
    """Подсчет просмотра товаров"""

    users = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="products")
    data_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_at"]
        verbose_name = _("просмотр продута")
        verbose_name_plural = _("просмотр продуктов")


class Status(models.TextChoices):
    pending = "pending", "В ожидании"
    running = "running", "В процессе выполнения"
    completed = "completed", "Выполнен"
    failed = "failed", "Завершен с ошибкой"


class Import(models.Model):
    """модель для импорта товаров и отслеживания статуса выполнения"""

    # STATUS_CHOICES = (
    #     ('pending', 'В ожидании'),
    #     ('running', 'В процессе выполнения'),
    #     ('completed', 'Выполнен'),
    #     ('failed', 'Завершен с ошибкой'),
    # )

    source = models.CharField(max_length=255, verbose_name=_("имя файла или URL для импорта"))
    start_time = models.DateTimeField(null=True, verbose_name=_("дата и время начала импорта"))
    end_time = models.DateTimeField(null=True, verbose_name=_("дата и время окончания импорта"))
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.pending,
        verbose_name=_("статус импорта"),
    )
    imported_count = models.IntegerField(default=0, verbose_name=_("количество импортированных товаров"))
    errors = models.JSONField(default=list, verbose_name=_("список ошибок при импорте"))
    email = models.EmailField(null=True, verbose_name=_("email получателя уведомления"))
    task_id = models.CharField(max_length=36, blank=True, null=True, verbose_name=_("идентификатор задачи"))

    def __str__(self):
        return f"Импорт из {self.source}"

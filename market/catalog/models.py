from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from catalog import utilites
from catalog.cache_for_catalog import clear_cache_category


class Catalog(models.Model):
    """Категории каталога"""

    name = models.CharField(max_length=100, help_text=_("наименование"))
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    image = models.FileField(upload_to="catalog/icon/", verbose_name=_("картинка"))
    is_featured = models.BooleanField(default=False, verbose_name=_("избранная категория"))
    slug = models.SlugField(max_length=256, blank=True, verbose_name=_("slug"))

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = utilites.get_slug(self.name)
        clear_cache_category()
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:catalog-category", kwargs={"slug": self.slug})

    class Meta:
        verbose_name = _("категория")
        verbose_name_plural = _("категории")
        ordering = [
            "name",
        ]

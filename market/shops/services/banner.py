from ..models import Banner
from site_settings.models import SiteSettings


def banner():
    """Функция для главной страницы для вывода трёх случайных активных баннеров.
     Баннеры закешированы на десять минут"""
    site_settings = SiteSettings.load()
    random_banners = Banner.objects.filter(active=True).order_by('?')[:site_settings.banners_count]
    return random_banners

from products.models import Browsing_history
from site_settings.models import SiteSettings
import datetime


def is_valid_history(user_id, product_id):
    """Проверка на просмотр продукта"""
    try:
        update_date = Browsing_history.objects.get(users_id=user_id, product_id=product_id)
        update_date.data_at = datetime.datetime.now()
        update_date.save()
        return True
    except Browsing_history.DoesNotExist:
        return False


def browsing_history(user_id, product_id):
    """Добавление продукта в список просмотренных"""
    try:
        site_settings = SiteSettings.load()

        # Получаем список просмотренных товаров для пользователя
        history = Browsing_history.objects.filter(users_id=user_id)

        # Если список просмотренных товаров для пользователя больше значения в настройках,
        # то удаляем самый первый просмотренный товар
        if history.count() >= site_settings.maximum_number_of_viewed_products:
            history.order_by('data_at').first().delete()
        Browsing_history.objects.create(users_id=user_id,
                                        product_id=product_id)
    except Browsing_history.DoesNotExist:
        Browsing_history.objects.create(users_id=user_id, product_id=product_id)

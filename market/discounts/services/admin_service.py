from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


def formatted_last_time_service(obj):
    """Функция для отображения окончания действия скидки"""
    last_time = obj.last_discount_time
    "Если срок действия скидки <= 0, выводится значение "
    if last_time.total_seconds() > 0:
        return last_time

    return mark_safe(f'<span style="color: red;">{_("Время действия скидки истекло !")}</span>')

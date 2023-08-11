from django.contrib.auth import update_session_auth_hash, login
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from users.models import UserAvatar
from shops.models import OrderOffer


def last_order_request(user):
    """Возвращает последний заказ если он есть"""
    order = OrderOffer.objects.filter(offer__orders__custom_user=user).last()
    return order


class MyProfileService:
    """Класс сервисов для работы с user views"""

    @staticmethod
    def form_validation(form, request, second_form=None):
        """Метод для проверки формы и сохранения данных профиля"""
        if form.cleaned_data.get("new_password1") and form.cleaned_data.get("new_password2"):
            form.save()
            update_session_auth_hash(request, form.user)
            login(request, form.user)
        second_form.save()
        success_message = _("Профиль успешно сохранен")
        return redirect(reverse("users:users_profile") + "?success_message=" + success_message)

    @staticmethod
    def post_form_validation(form, second_form, request):
        """Метод для проверки формы при и сохранения аватара"""
        if form.is_valid() and second_form.is_valid():
            select_avatar = second_form.cleaned_data.get("avatar")
            if select_avatar:
                avatar = UserAvatar.objects.filter(user_id=request.user.pk).first()
                if not avatar:
                    avatar = UserAvatar.objects.create(user=request.user)
                avatar.image = select_avatar
                avatar.save()
            return True

from products.models import Browsing_history
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.contrib.auth.views import LoginView, LogoutView, FormView
from django.views.generic import CreateView
from django.views.generic.base import View
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser, UserAvatar
from users import forms
from users.services.profile import ProfileMixin
from users.services.users_service import last_order_request
from site_settings.models import SiteSettings


class UserRegistrationView(CreateView):
    """Регистрация нового пользователя"""

    form_class = forms.CustomUserCreationForm
    model = CustomUser
    template_name = "market/users/register.jinja2"
    success_url = "/"

    def form_valid(self, form):
        result = super().form_valid(form)
        default_avatar = UserAvatar.objects.create(
            image="users/avatars/default/default_avatar1.png", user_id=self.object.id
        )
        default_avatar.save()
        return result


class MyLoginView(LoginView):
    """Вход пользователя"""

    LoginView.next_page = reverse_lazy("index")
    redirect_authenticated_user = True
    template_name = "market/users/login.jinja2"
    authentication_form = forms.CustomAuthenticationForm


class UserLogoutView(LogoutView):
    """Выход пользователя"""

    next_page = reverse_lazy("users:users_login")


class RestorePasswordView(FormView):
    """Восстановление пароля пользователя"""

    form_class = forms.RestorePasswordForm
    template_name = "market/users/password.jinja2"
    success_url = reverse_lazy("users:users_restore_password")

    def form_valid(self, form):
        """Проверка валидности формы"""
        super().form_valid(form)
        user_email = form.cleaned_data["email"]
        new_password = CustomUser.objects.make_random_password()
        current_user = CustomUser.objects.filter(email__exact=user_email).first()
        current_user.set_password(new_password)
        current_user.save()
        send_mail(
            subject="Password reset instructions",
            message=f"New password: {new_password}",
            from_email="admin@gmail.com",
            recipient_list=[form.cleaned_data["email"]],
        )
        success_message = _(f"Новый пароль успешно отправлен на {user_email}")
        return redirect(reverse_lazy("users:users_restore_password") + "?success_message=" + success_message)


class AccountView(View):
    """Личный кабинет"""

    def get(self, request):
        user_account = get_object_or_404(CustomUser, email=request.user.email)
        if user_account.email != request.user.email:
            return render(request, "market/base.jinja2")
        user = CustomUser.objects.get(pk=request.user.pk)
        if user.first_name and user.last_name:
            name = f"{user.first_name} {user.last_name}"
        else:
            name = user.username
        context = {
            "username": name,
            "user": user,
            "order": last_order_request(request.user),
        }
        return render(request, "market/users/account.jinja2", context)


class MyProfileView(ProfileMixin):
    pass


class BrowsingHistory(View):
    """Контроллер истории просмотров товаров"""

    def get(self, request):
        site_settings = SiteSettings.load()
        history = Browsing_history.objects.filter(users_id=request.user.id).order_by("-data_at")[
                  :site_settings.maximum_number_of_viewed_products]
        history_count = Browsing_history.objects.count()
        contex = {"count": history_count, "history": history}
        return render(request, "market/users/browsing_history.jinja2", context=contex)

    def post(self, request):
        site_settings = SiteSettings.load()
        product_id = self.request.POST.get("delete")
        history = Browsing_history.objects.all().order_by("-data_at")[:site_settings.maximum_number_of_viewed_products]
        if "delete" in request.POST:
            Browsing_history.objects.filter(product_id=product_id).delete()
        history_count = Browsing_history.objects.count()
        contex = {"count": history_count, "history": history}
        return render(request, "market/users/browsing_history.jinja2", context=contex)

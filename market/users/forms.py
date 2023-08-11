from django import forms
from django.contrib.auth.forms import (
    BaseUserCreationForm,
    AuthenticationForm,
    UserChangeForm,
)
from django.core.exceptions import ValidationError
from users.models import CustomUser
from users.validators import PhoneNumberValidator, ValidateImageSize
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
from django.core import validators
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import password_validation


def emai_existed_validator(value):
    """Проверка существования пользователя по email"""
    if not CustomUser.objects.filter(email__exact=value).first():
        raise ValidationError(f"Пользователь {value} не найден.")


class LowerEmailField(forms.EmailField):
    """Запись email в нижнем регистре"""

    def to_python(self, value):
        value = super().to_python(value)
        if value is not None:
            value = value.lower()
        return value


class CustomUserCreationForm(BaseUserCreationForm):
    """Форма для создания нового пользователя"""

    class Meta:
        model = CustomUser
        fields = "email", "username"


class CustomAuthenticationForm(AuthenticationForm):
    """Форма для входа пользователя"""

    def clean(self):
        """Перевод имени пользователя в нижний регистр"""
        username = self.cleaned_data.get("username")
        username = username.lower()
        password = self.cleaned_data.get("password")

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()

            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class RestorePasswordForm(forms.Form):
    """Форма восстановления пароля"""

    email = LowerEmailField(
        required=True,
        validators=[emai_existed_validator],
        help_text=_("Укажите email пользователя"),
    )


class ChangePasswordForm(SetPasswordForm):
    """Форма изменения пароля"""

    new_password1 = forms.CharField(
        required=False,
        label=_("новый пароль"),
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
        strip=False,
    )
    new_password2 = forms.CharField(
        required=False,
        label=_("подтверждение нового пароля"),
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
    )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Пароли не совпадают"))
        elif password1 and password2:
            password_validation.validate_password(password2, self.user)
            return password2
        return None


class UserProfileForm(UserChangeForm):
    """Форма редактирования профиля"""

    phone_validator = PhoneNumberValidator()
    validate_image_size = ValidateImageSize()

    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-label"}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-label"}))
    phone_number = forms.CharField(
        required=False,
        validators=[phone_validator],
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-label"}),
    )
    avatar = forms.ImageField(
        required=False,
        validators=[validate_image_size, validators.validate_image_file_extension],
        widget=forms.FileInput(attrs={"class": "Profile-file form-input"}),
    )
    email = LowerEmailField(required=False, widget=forms.TextInput(attrs={"class": "form-label"}))

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "phone_number", "email", "avatar")

    def clean_email(self):
        email = self.cleaned_data["email"]
        user = CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).first()
        if user:
            raise ValidationError(_("Этот электронный адрес уже используется."))
        return email

    def clean_phone_number(self):
        """Валидация данных и проверка отсутствия номера телефона в базе данных"""
        phone_number = self.cleaned_data["phone_number"]
        user = CustomUser.objects.filter(phone_number=phone_number).exclude(pk=self.instance.pk).first()
        if user and user.phone_number != "+0000000000":
            raise ValidationError(f"Пользователь с номером {user.phone_number} уже существует.")
        return phone_number

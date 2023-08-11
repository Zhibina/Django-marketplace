import re
from django.core.exceptions import ValidationError
from django.contrib.auth.models import UserManager
from django.core import validators
from django.utils.translation import gettext_lazy as _
from django.core.validators import deconstructible


@deconstructible()
class PhoneNumberValidator(validators.RegexValidator):
    """Проверка формата номера телефона"""

    regex = r"^\+\d+$"
    message = _("Номер телефона должен начинаться с + и содержать только цифры")
    flags = 0


@deconstructible()
class ValidateImageSize:
    """Проверка допустимого размера файла"""

    max_size = 2 * 1024**2

    def __call__(self, image):
        if image.size > self.max_size:
            raise ValidationError(_("Размер файла превышает допустимое значение 2 MB."))


class CustomUserManager(UserManager):
    use_in_migrations = True

    @classmethod
    def validate_email(cls, email):
        """Проверка корректности ввода email"""
        regex = r"^[a-zA-Z0-9._]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(regex, email) is not None

    @classmethod
    def normalize_email(cls, email):
        """Перевод email в нижний регистр"""
        email = email or ""
        if cls.validate_email(email):
            email = email.lower()
            return email

        raise ValidationError(_("Введите корректный email адрес"))

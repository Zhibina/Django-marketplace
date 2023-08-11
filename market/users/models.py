from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core import validators
from django.core.exceptions import ValidationError
from users.validators import PhoneNumberValidator, CustomUserManager, ValidateImageSize


def user_avatar_directory_path(instance, filename: str) -> str:
    """Путь для сохранения аватара пользователя"""
    return f"users/avatars/user_{instance.pk}/{filename}"


def get_default_avatar_path():
    """Путь к аватару пользователя по умолчанию"""
    return "users/avatars/default/default_avatar1.png"


class CustomUser(AbstractUser):
    """Класс пользователя"""

    phone_number_validator = PhoneNumberValidator()

    objects = CustomUserManager()

    email = models.EmailField(_("email"), blank=False, null=False, unique=True)
    phone_number = models.CharField(
        max_length=20,
        help_text=_("номер телефона должен начинаться с + и содержать только цифры"),
        validators=[phone_number_validator],
        null=False,
        default="+0000000000",
        verbose_name=_("номер телефона"),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def clean(self):
        """Валидация данных и проверка отсутствия номера телефона в базе данных"""
        super().clean()
        user = CustomUser.objects.filter(phone_number=self.phone_number).exclude(id=self.id).first()
        if user and user.phone_number != "+0000000000":
            raise ValidationError(f"Пользователь с номером {user.phone_number} уже существует.")

    class Meta:
        verbose_name = _("пользователь")
        verbose_name_plural = _("пользователи")


class UserAvatar(models.Model):
    validate_image_size = ValidateImageSize()
    image = models.ImageField(
        null=False,
        blank=False,
        upload_to=user_avatar_directory_path,
        default=get_default_avatar_path,
        validators=[validators.validate_image_file_extension, validate_image_size],
        verbose_name=_("фото профиля"),
    )
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="avatar")

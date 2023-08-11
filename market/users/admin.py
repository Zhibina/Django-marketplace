from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from users.forms import CustomUserCreationForm
from users.models import CustomUser, UserAvatar


class UserAvatarInline(admin.TabularInline):
    model = UserAvatar


@admin.register(CustomUser)
class AccountAdmin(UserAdmin):
    inlines = [UserAvatarInline]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("личная информация"),
            {"fields": ("username", "first_name", "last_name", "phone_number")},
        ),
        (
            _("разрешения"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("важные даты"), {"fields": ("last_login", "date_joined")}),
    )

    add_form = CustomUserCreationForm
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
    )

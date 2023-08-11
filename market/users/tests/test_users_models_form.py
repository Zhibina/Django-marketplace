import os
import shutil
from django.test import TestCase
from django.urls import reverse_lazy, reverse
from users.models import CustomUser, PhoneNumberValidator, UserAvatar

from django.contrib.auth.hashers import check_password
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

from users.forms import UserProfileForm, ChangePasswordForm


class UserProfileTest(TestCase):
    """Создание профиля"""

    @classmethod
    def setUpClass(cls):
        """Создание пользователя"""
        super().setUpClass()
        cls.credentials = {"username": "test1@admin.com", "password": "123"}
        cls.user = CustomUser.objects.create_user(username="test_user", email="test1@admin.com", password="123")

    @classmethod
    def tearDownClass(cls):
        """Удаление пользователя"""
        super().tearDownClass()
        cls.user.delete()

    def test_custom_user_data(self):
        """Проверка данных профиля созданного пользователя"""

        self.client.post("/login/", self.credentials, follow=True)
        avatar_user = UserAvatar.objects.create(
            image="users/avatars/default/default_avatar1.png", user_id=self.user.pk
        )
        avatar = self.user.avatar.image
        phone = self.user.phone_number
        self.assertEqual(avatar, "users/avatars/default/default_avatar1.png")
        self.assertEqual(avatar_user.image, "users/avatars/default/default_avatar1.png")
        self.assertEqual(phone, "+0000000000")


class RegistrationFormTest(TestCase):
    """Проверка страницы регистрации и входа"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test_user@example.com", username="Admin12", password="Pass123456"
        )

        self.url = reverse_lazy("users:users_register")
        self.data1 = {
            "username": "test_user",
            "email": "test_user22@example.com",
            "password1": "Pass123456",
            "password2": "Pass123456",
        }

        self.data2 = {
            "username": "test_user1",
            "first_name": "Test1",
            "last_name": "User1",
            "email": "Test_user@example.com",
            "password1": "Pass123456",
            "password2": "Pass123456",
        }

    def tearDown(self) -> None:
        self.user.delete()

    def test_registration_form(self):
        """Проверка формы регистрации"""
        response = self.client.post(self.url, data=self.data1)
        self.assertEqual(response.status_code, 302)
        user = CustomUser.objects.get(username=self.data1["username"])
        self.assertEqual(user.email, self.data1["email"])
        self.assertEqual(user.phone_number, "+0000000000")
        self.assertEqual(user.avatar.image, "users/avatars/default/default_avatar1.png")

    def test_login(self):
        """Проверка входа"""
        login_data = {"username": "test_user@example.com", "password": "Pass123456"}
        response = self.client.post(reverse_lazy("users:users_login"), login_data)
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse_lazy("users:users_logout"))
        self.assertEqual(response.status_code, 302)

        login_data = {"username": "TeSt_uSEr@example.com", "password": "Pass123456"}
        response = self.client.post(reverse_lazy("users:users_login"), login_data)
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse_lazy("users:users_logout"))
        self.assertEqual(response.status_code, 302)

        login_data = {"username": "TeSt_uSEr@example.com", "password": "Pass12345"}
        response = self.client.post(reverse_lazy("users:users_login"), login_data)
        self.assertContains(
            response,
            "Please enter a correct email and password." " Note that both fields may be case-sensitive.",
        )

    def test_logout(self):
        """Проверка url выхода пользователя"""
        response = self.client.post(reverse_lazy("users:users_logout"))
        self.assertEqual(response.status_code, 302)


class UserProfileChangeTests(TestCase):
    """Проверка страницы профиля"""

    @classmethod
    def setUpClass(cls):
        """Создание пользователя"""
        super().setUpClass()
        cls.user = CustomUser.objects.create_user(
            username="testuser", email="testuser@gmail.com", password="testpass123"
        )
        cls.credentials_user1 = {"username": "testuser@gmail.com", "password": "testpass123"}
        cls.user2 = CustomUser.objects.create_user(
            email="test_user@example.com", username="Admin12", password="Pass123456"
        )
        cls.credentials_user2 = {"username": "test_user@example.com", "password": "Pass123456"}
        cls.url = reverse_lazy("users:users_profile")

    @classmethod
    def tearDownClass(cls):
        """Удаление пользователя"""
        super().tearDownClass()
        cls.user.delete()
        cls.user2.delete()

    def test_edit_profile_view_success(self):
        """Проверка формы редактирования профиля"""
        self.client.post(reverse("users:users_login"), self.credentials_user1, follow=True)
        avatar_user = UserAvatar.objects.create(
            image="users/avatars/default/default_avatar1.png", user_id=self.user.pk
        )

        new_email = "newemail@gmail.com"
        new_phone_number = "+0987654321"
        new_first_name = "Test"
        new_last_name = "UserTest"
        file = BytesIO()
        image = Image.new("RGBA", size=(1024, 1024), color=(155, 0, 0))
        image.save(file, "png")
        file.seek(0)
        avatar = SimpleUploadedFile("test_avatar.png", file.getvalue(), content_type="image/png")

        test_data = {
            "email": new_email,
            "phone_number": new_phone_number,
            "avatar": avatar,
            "first_name": new_first_name,
            "last_name": new_last_name,
        }
        response = self.client.post(reverse("users:users_profile"), test_data)

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        avatar_user.user.refresh_from_db()
        self.assertEqual(self.user.email, new_email)
        self.assertEqual(self.user.phone_number, new_phone_number)
        self.assertEqual(self.user.first_name, new_first_name)
        self.assertEqual(self.user.last_name, new_last_name)
        self.assertTrue(check_password("testpass123", self.user.password))
        self.assertIsNotNone(self.user.avatar.image)
        self.assertEqual(self.user.avatar.image.width, 1024)
        self.assertEqual(self.user.avatar.image.height, 1024)
        self.assertLessEqual(self.user.avatar.image.size, 2 * 1024 * 1024)
        avatar_directory = os.path.dirname(self.user.avatar.image.path)
        shutil.rmtree(avatar_directory)

    def test_edit_profile_form_failure(self):
        """Проверка валидации с некорректными данными"""
        form_data = {
            "phone_number": "1234567890",
            "email": "test_user@example.com",
        }
        form = UserProfileForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "phone_number", PhoneNumberValidator.message)
        self.assertEqual(form.errors["email"], ["Этот электронный адрес уже используется."])

    def test_change_password_form_success(self):
        """Проверка формы изменения пароля"""
        self.client.post("/users/login/", self.credentials_user1, follow=True)
        new_password = "newpass123"
        form_data = {"new_password1": new_password, "new_password2": new_password}
        form = ChangePasswordForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())
        self.assertIsNotNone(form.cleaned_data["new_password2"])
        self.assertTrue(self.user.check_password("testpass123"))
        if form.is_valid():
            form.save()
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))

    def test_change_password_form_failure(self):
        """Проверка валидации с некорректными данными"""
        invalid_password1 = "testpass123"
        form = ChangePasswordForm(
            user=self.user, data={"new_password1": "newpass123", "new_password2": invalid_password1}
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["new_password2"], ["Пароли не совпадают"])

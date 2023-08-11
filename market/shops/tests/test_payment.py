from django.test import TestCase
from django.urls import reverse

from shops.tests.test_comparison import CompareTestCase
from users.models import CustomUser


class PaymentTestCase(TestCase):
    """Тест проверки работы оплаты"""

    fixtures = CompareTestCase.fixtures | {
        "fixtures/050_order_status.json",
        "fixtures/055_order.json",
    }
    login_url = "/users/login/"

    def setUp(self) -> None:
        self.user = CustomUser.objects.get(pk=11)
        self.credentials = {"username": self.user.email, "password": self.user.password}
        login_data = {
            "username": self.user.email,
            "password": "123",
        }
        self.client.post(self.login_url, login_data)

    def test_payment_view_success(self):
        """Проверка отображения страницы"""
        response = self.client.get(reverse("payment", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)

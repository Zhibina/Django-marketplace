from django.test import TestCase
from django.urls import reverse

from shops.models import Order
from shops.services.order import pryce_delivery, save_order_model
from shops.tests.test_comparison import CompareTestCase
from users.models import CustomUser


class OrderTestCase(TestCase):
    """Тест проверки работы заказов"""

    fixtures = CompareTestCase.fixtures | {
        "fixtures/050_order_status.json",
        "fixtures/055_order.json",
        "fixtures/065_order_offer.json",
        "fixtures/070_order_status_change.json",
        "shops/tests/cart_damp.json",
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
        self.client.session["cart"] = {}

    def test_history_order_view_success(self):
        """Тестирование истории заказа"""
        self.client.post(reverse("users:users_login"), self.credentials, follow=True)
        order = Order.objects.filter(custom_user=self.user)
        response = self.client.get(reverse("order_history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"№{order[0].id}")
        self.assertContains(response, f"№{order[1].id}")

    def test_order_details_view_success(self):
        """Тестирование детального отображения заказа"""
        self.client.post("/users/login/", self.credentials, follow=True)
        order = Order.objects.filter(custom_user=self.user)
        response = self.client.get(reverse("order_details", kwargs={"pk": order[0].id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order[0].address)

    def test_pryce_delivery_saccess(self):
        """Тестирование срабатывания функции"""
        result = pryce_delivery(self.user)
        self.assertEqual(len(result), 5)

    def test_save_order_model_saccess(self):
        """Проверка создания  нового заказа"""
        forma_order = {"delivery": "ORDINARY", "city": "Москва", "address": "Пупкина 4", "pay": "ONLINE"}
        expected_result1 = Order.objects.all().count() + 1
        save_order_model(self.user, forma_order, self.client.session)
        self.assertEqual(expected_result1, Order.objects.all().count())

    def test_create_order_view_success(self):
        """Проверка отображения страницы"""
        response = self.client.get(reverse("order"))
        self.assertEqual(response.status_code, 200)

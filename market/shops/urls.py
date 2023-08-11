from django.urls import path
from django.conf import settings
from django.views.decorators.cache import cache_page # noqa 401
from .views import (
    BaseView,
    seller_detail,
    home,
    ComparePageView,
    CreateOrderView,
    OrderLoginView,
    HistoryOrderView,
    OrderDetailsView,
    PaymentView,
    process_payment,
)

urlpatterns = [
    path("", BaseView.as_view(), name="index"),
    path("comparison/", ComparePageView.as_view(), name="comparison"),
    path("home/", cache_page(settings.CACHE_CONSTANT, key_prefix='home')(home), name="home"),
    path("seller/", seller_detail, name="seller_detail"),
    path("order/", CreateOrderView.as_view(), name="order"),
    path("order/login/", OrderLoginView.as_view(), name="order_login"),
    path("order_history/", HistoryOrderView.as_view(), name="order_history"),
    path("order_history/<int:pk>/", OrderDetailsView.as_view(), name="order_details"),
    path("payment/<int:pk>/", PaymentView.as_view(), name="payment"),
    path("pay/", process_payment, name="pay"),
]

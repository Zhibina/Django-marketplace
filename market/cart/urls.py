from django.urls import path
from .views import CartView, cart_add, delete_item_from_cart

app_name = "cart"

urlpatterns = [
    path("cart_items/", CartView.as_view(), name="cart_items"),
    path("add/<int:pk>/<int:silent>", cart_add, name="cart_add"),
    path("delete/<int:pk>", delete_item_from_cart, name="delete_from_cart"),
]

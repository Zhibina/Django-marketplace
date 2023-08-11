from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView

from shops.models import Offer
from cart.cart import Cart as CartServices


class CartView(TemplateView):
    """Страница корзины"""

    template_name = "market/cart/cart.jinja2"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = CartServices(self.request)
        context["cart"] = cart
        return context


def cart_add(request, pk, silent):
    """Добавляем товар в корзину"""
    cart = CartServices(request)
    offer = get_object_or_404(Offer, id=pk)
    cart.add_to_cart(offer=offer)
    if not silent:
        return redirect("cart:cart_items")
    else:
        return redirect(request.META.get("HTTP_REFERER"))


def delete_item_from_cart(request, pk):
    """Удаляем товар из корзины"""
    cart = CartServices(request)
    offer = get_object_or_404(Offer, id=pk)
    cart.delete_from_cart(offer=offer)
    return redirect(request.META.get("HTTP_REFERER"))

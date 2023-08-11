from django.contrib.auth import user_logged_in
from django.dispatch import receiver
from cart.cart import Cart


@receiver(user_logged_in)
def after_user_logged_in(request, sender, user, **kwargs):
    """Отслеживаем сигнал входа пользователя на сайт и добавляем корзину в бд или в сессию"""
    cart = Cart(request)
    if cart.get_products_quantity() == 0:
        cart.save_to_session()
    else:
        cart.save_to_db()

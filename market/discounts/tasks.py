from discounts.models import ShopItemDiscount, CartItemDiscount
from config.celery import app


@app.task(name="check_discounts_last_time", bind=True)
def check_discounts_last_time():
    """Function to check last time of discounts"""
    shop_discounts = ShopItemDiscount.objects.filter(active=True).all()
    cart_discounts = CartItemDiscount.objects.filter(active=True).all()

    deactivated = [
        discount.last_discount_time
        for discounts in (shop_discounts, cart_discounts)
        for discount in discounts
        if discount is not None
    ]

    if deactivated:
        print("Discounts deactivated:", deactivated)

class OfferDiscount:
    """Класс для получения скидки для продукта в офере"""

    def __init__(self, offer):
        self.offer = offer
        self.price = offer.price
        self.product_category = offer.product.category
        self.product = offer.product

    def __call__(self, *args, **kwargs):
        discount = self.get_all_discounts()
        return discount

    def get_product_discount(self, discounts, **kwargs):
        """Метод для получения максимальной скидки"""
        discount = max(
            [
                discount.discount_amount
                if discount.discount_amount_type == 2
                else self.price / 100 * discount.discount_amount
                for discount in discounts.filter(active=True, **kwargs)
            ],
            default=0,
        )
        return discount

    def get_all_discounts(self):
        """Метод для получения максимальной скидки из всех возможных"""
        product_discount = self.product.shopitemdiscount
        product_category_discount = self.product_category.shopitemdiscount
        max_discount = max(
            self.get_product_discount(product_discount), self.get_product_discount(product_category_discount)
        )
        return max_discount

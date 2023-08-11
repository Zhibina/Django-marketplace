from django.db.models import Q
from discounts.models import CartItemDiscount
from cart.cart import Cart


class DiscountService:
    """Класс для расчета скидок на товары в корзине"""

    def __init__(self, cart: Cart):
        self.cart = cart
        self.products = self.cart.get_products()
        self.total_price = self.cart.get_total_price()
        self.total_quantity = self.cart.get_products_quantity()
        self._products_wit_shop_discount = dict()
        self._products_wit_cart_discount = dict()
        self._total_price_with_discount = self._get_max_discount()

    @property
    def get_product_with_new_price(self) -> dict:
        """Метод возвращает словарь с продуктами, которые получили скидки"""
        return self._products_wit_shop_discount or self._products_wit_cart_discount

    @property
    def get_total_price_with_discount(self):
        """ "Метод возвращает итоговую стоимость корзины с учетом скидки"""
        return self._total_price_with_discount

    def discounts_handler(self, discounts, values, **kwargs):
        """Метод для получения списка скидок на товар"""
        products_quantity = values.get("pcs")
        product_price = values.get("unit_price")

        discount = (
            max(
                [
                    discount.discount_amount
                    if discount.discount_amount_type == 2
                    else round(product_price / 100 * float(discount.discount_amount), 2)
                    for discount in discounts.filter(active=True, **kwargs)
                ],
                default=0,
            )
            * products_quantity
        )
        return discount

    def _get_shop_discount(self) -> int:
        """Метод для нахождения максимальной скидки установленной магазином на товары"""

        shop_products = {}
        for product, values in self.products.items():
            products_quantity = values.get("pcs")
            product_price = values.get("unit_price")
            total_units_price = products_quantity * product_price
            product_discount = self.discounts_handler(product.shopitemdiscount, values)
            category_discount = self.discounts_handler(product.category.shopitemdiscount, values)

            if product_discount or category_discount:
                products_discount = max(product_discount, category_discount)

                shop_products[product] = products_discount
                self._products_wit_shop_discount[product] = (
                    total_units_price - products_discount if total_units_price > products_discount else 1
                )

        total_discount = sum(shop_products.values())
        return total_discount

    def _get_cart_discount_with_products(self) -> int:
        """Метод для расчета максимальной скидки для корзины
        В методе высчитываются варианты скидки, для которых указаны продукты и их категории"""

        cart_products_discount = {}

        categories = {product.category for product in self.products.keys()}

        for product, values in self.products.items():
            var1 = self.discounts_handler(product.cartitemdiscount, values, categories__in=categories)
            var2 = self.discounts_handler(
                product.cartitemdiscount,
                values,
                categories__in=categories,
                total_price_of_cart__gte=self.total_price,
                amount_product_in_cart__gte=self.total_quantity,
            )
            var3 = self.discounts_handler(
                product.cartitemdiscount,
                values,
                categories__in=categories,
                total_price_of_cart=None,
                amount_product_in_cart__gte=self.total_quantity,
            )

            var4 = self.discounts_handler(
                product.cartitemdiscount,
                values,
                categories__in=categories,
                total_price_of_cart__gte=self.total_price,
                amount_product_in_cart=None,
            )

            if var1 or var2 or var3 or var4:
                unit_price = values.get("unit_price")
                max_discount = max(var1, var2, var3, var4)
                cart_products_discount[product] = max_discount
                self._products_wit_cart_discount[product] = (
                    unit_price - max_discount if unit_price > max_discount else 1
                )

        cart_products_discount = sum(cart_products_discount.values())
        return cart_products_discount

    def _get_cart_discount(self) -> int:
        """Метод для расчета максимальной скидки из всех возможных скидок для корзины"""

        common_kwargs = {"active": True, "products": None, "categories": None}

        discount_for_cart = CartItemDiscount.objects.filter(
            Q(
                **common_kwargs,
                total_price_of_cart=None,
                amount_product_in_cart__lte=self.total_quantity,
            )
            | Q(
                **common_kwargs,
                total_price_of_cart__lte=self.total_price,
                amount_product_in_cart__lte=self.total_quantity,
            )
            | Q(
                **common_kwargs,
                total_price_of_cart__lte=self.total_price,
                amount_product_in_cart=None,
            )
        )

        max_cart_discount = max(
            [
                discount.discount_amount
                if discount.discount_amount_type == 2
                else round(self.total_price / 100 * float(discount.discount_amount), 2)
                for discount in discount_for_cart
            ],
            default=0,
        )
        return max(max_cart_discount, self._get_cart_discount_with_products())

    def _get_max_discount(self) -> int:
        """Метод для получения максимально возможной скидки.
        Если размер скидки превышает стоимость корзины, то возвращается
        цена корзины равная 1 либо количеству товаров с ценой 1.
        """
        total_price = self.total_price

        max_shop_discount = self._get_shop_discount()
        max_cart_discount = self._get_cart_discount()

        if max_shop_discount > max_cart_discount:
            self._products_wit_cart_discount = {}
            if max_shop_discount > total_price:
                return len(self._products_wit_shop_discount.values())
            return total_price - max_shop_discount

        self._products_wit_discount = {}
        if max_cart_discount > total_price:
            return 1
        return total_price - max_cart_discount

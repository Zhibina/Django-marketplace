from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from discounts.models import ShopItemDiscount, CartItemDiscount


class ShopDiscountCreationForm(forms.ModelForm):
    """Форма для создания записи в таблице скидок для магазина"""

    discount_amount = forms.DecimalField(min_value=1, max_digits=10, decimal_places=2)

    class Meta:
        model = ShopItemDiscount
        fields = "__all__"

    def clean(self):
        """Функция проверки введенных данных"""
        cleaned_data = super().clean()

        if "total_price_of_cart" not in cleaned_data:
            if not (cleaned_data.get("products") or cleaned_data.get("categories")):
                self.add_error(None, _("Заполните хотя бы одно поле для категории или товаров"))

        discount_amount = cleaned_data.get("discount_amount")
        discount_amount_type = cleaned_data.get("discount_amount_type")
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date < timezone.now():
            cleaned_data["start_date"] = timezone.now()

        if start_date > end_date:
            self.add_error(
                "end_date",
                _("Дата окончания действия скидки должна быть больше даты начала действия скидки"),
            )

        if discount_amount_type == 1 and discount_amount > 99:
            self.add_error("discount_amount", _("Скидка в % не должна превышать 99 %"))
        return cleaned_data


class CartDiscountCreationForm(ShopDiscountCreationForm):
    """Форма для создания записи в таблице скидок для корзины"""

    class Meta:
        model = CartItemDiscount
        fields = "__all__"

    def clean(self):
        """Функция проверки введенных данных"""
        cleaned_data = super().clean()

        if "total_price_of_cart" in cleaned_data and (cleaned_data.get("products") or cleaned_data.get("categories")):
            if cleaned_data.get("products"):
                self.add_error(
                    "categories",
                    _("При выборе продукта поле категории товаров должно быть заполнено "),
                )
            elif cleaned_data.get("categories"):
                self.add_error(
                    "products",
                    _("При выборе категории поле товары должно быть заполнено"),
                )

        if not (
            cleaned_data.get("categories")
            or cleaned_data.get("products")
            or cleaned_data.get("total_price_of_cart")
            or cleaned_data.get("amount_product_in_cart")
        ):
            self.add_error(None, _("Заполните хотя бы одно условие для получения скидки"))

        return cleaned_data

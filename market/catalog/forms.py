from django import forms
from django.utils.translation import gettext_lazy as _


class ProductFilterForm(forms.Form):
    """Форма заполнения фильтров"""

    price = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "range-line",
                "type": "text",
                "data-type": "double",
                "data-min": "5000",
                "data-max": "20000",
                "data-from": "6000",
                "data-to": "10000",
            }
        ),
    )
    name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("Название")}),
    )
    in_stock = forms.BooleanField(required=False)
    free_delivery = forms.BooleanField(required=False)

from django import forms

from shops.models import PaymentQueue, validate_card_number


class OderLoginUserForm(forms.Form):
    """Форма для логирования пользователя"""

    email = forms.EmailField(widget=forms.EmailInput)
    password = forms.CharField(
        widget=forms.PasswordInput,
        max_length=100,
    )


class PaymentForm(forms.ModelForm):
    """Форма для номера карты оплаты"""

    card_number = forms.IntegerField(validators=[validate_card_number])

    class Meta:
        model = PaymentQueue
        fields = [
            "card_number",
        ]

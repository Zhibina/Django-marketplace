from django import forms
from django.forms import FileInput

from .models import Review, Import


class ReviewFrom(forms.ModelForm):
    """Форма для добавления отзыва о продукте"""

    rating = forms.IntegerField(min_value=1, max_value=5, required=True)
    review_text = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}), required=True)

    class Meta:
        model = Review
        fields = ["rating", "review_text"]


class ImportForm(forms.ModelForm):
    """класс для формы импорта данных"""

    class Meta:
        """метакласс для указания модели и полей, которые будут включены в форму"""

        model = Import  # модель для формы
        fields = ["source", "email"]  # поля для формы

    def __init__(self, *args, **kwargs):
        """метод для инициализации формы"""
        super().__init__(*args, **kwargs)  # вызываем родительский метод
        self.fields["source"].label = "Your json file"  # устанавливаем метку для поля source
        self.fields["email"].label = "Email получателя уведомления"  # устанавливаем метку для поля email
        self.fields["email"].required = False  # делаем поле email необязательным для заполнения
        self.fields["source"].widget = FileInput(
            attrs={
                "class": "import_row",
                "accept": ".json",
            }
        )

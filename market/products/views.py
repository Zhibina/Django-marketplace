from django.shortcuts import render, redirect  # noqa F401
from django.views.generic import TemplateView, CreateView, DetailView
from django.urls import reverse
from django.http import JsonResponse
from rest_framework.views import APIView
from celery.result import AsyncResult
from import_data.tasks import import_products
from .models import Review, Import
from .forms import ReviewFrom, ImportForm
from .services.product_services import ProductsServices


class ReviewsAPI(APIView):
    """Класс для отправки данных об отзывах через API"""

    def get(self, request):
        """Создание JSON для модели Review"""
        product_id = request.GET.get("product_id")
        offset = int(request.GET.get("offset", 0))
        limit = int(request.GET.get("limit", 3))
        reviews = Review.get_review(product_id=product_id)[offset : offset + limit]  # noqa F401
        data = [
            {
                "number": n + 1,
                "user": {
                    "id": r.user.id,
                    "username": r.user.username,
                    "firstname": r.user.first_name,
                    "lastname": r.user.last_name,
                    "avatar": r.user.avatar.image.url,
                },
                "product": r.product.name,
                "rating": r.rating,
                "text": r.review_text,
                "created": r.created_at,
            }
            for n, r in enumerate(reviews)
        ]
        return JsonResponse({"data": data})


class ProductView(TemplateView):
    """Класс для отображения деталей продукта"""

    template_name = "market/products/product_detail.jinja2"
    form_class = ReviewFrom

    def get_context_data(self, **kwargs):
        """Получение необходимого контекста"""
        services = ProductsServices(request=self.request, product_id=self.kwargs.get("product_id"))
        context = super().get_context_data(**kwargs)
        context.update(services.get_context(form=self.form_class()))
        return context

    def post(self, request, product_id):
        """Обработка добавления отзыва"""
        form = self.form_class(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user_id = request.user.id
            review.product_id = product_id
            review.save()
            return redirect("/")
        context = self.get_context_data(product_id=product_id)
        context["form"] = form
        return self.render_to_response(context)


class BaseView(TemplateView):
    template_name = "market/base.jinja2"


class ImportCreateView(CreateView):
    """представление для запуска импорта"""

    model = Import
    form_class = ImportForm
    template_name = "market/products/import_form.jinja2"

    def form_valid(self, form):
        # вызываем родительский метод для создания объекта модели Import с данными из формы
        response = super().form_valid(form)

        # получаем имя файла или URL и email из формы
        source = form.cleaned_data["source"]
        email = form.cleaned_data["email"]

        # запускаем задачу импорта с помощью celery
        task = import_products.delay(source, email)

        # получаем идентификатор задачи
        task_id = task.id

        # сохраняем идентификатор задачи в объекте модели Import
        self.object.task_id = task_id
        self.object.save()

        # перенаправляем пользователя на страницу с деталями импорта
        return response

    def get_success_url(self):
        # метод для получения URL для перенаправления после создания объекта модели Import
        return reverse("products:import-detail", kwargs={"pk": self.object.pk})


class ImportDetailView(DetailView):
    """представление для отображения деталей импорта"""

    model = Import
    template_name = "market/products/import_detail.jinja2"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        import_obj = self.get_object()
        task_id = import_obj.task_id
        # получаем статус и результат задачи с помощью celery
        task = AsyncResult(task_id)
        task_status = task.status
        if task_status == "SUCCESS":
            # task_result = task.result
            context["task_result"] = (
                f"Импорт из {import_obj.source} успешно завершен."
                f" Импортировано {import_obj.imported_count} товаров."
            )
        elif task_status == "FAILURE":
            context["task_result"] = f"Импорт из {import_obj.source} завершен с ошибкой. Ошибка: {task.result}"
        else:
            context["task_result"] = "Импорт еще не завершен"
        context["task_status"] = task_status
        context["start_time"] = import_obj.start_time
        context["end_time"] = import_obj.end_time
        context["status"] = import_obj.status
        return context

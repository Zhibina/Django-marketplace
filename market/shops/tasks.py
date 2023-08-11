import random
from datetime import datetime, time, timedelta
from celery import shared_task
from django.core.cache import cache
from products.models import Product
from shops.models import PaymentQueue, OrderStatus
from shops.services.fake_payment import FakePaymentService


@shared_task
def update_product_of_the_day(name="Task time left"):
    """таск для обновления времени каждые 24 часа и выбор рандомного продукта из ограниченного тиража"""
    now = datetime.now()
    midnight = datetime.combine(now.date(), time.min)
    time_left = (midnight + timedelta(days=1) - now).seconds
    products = Product.objects.filter(limited_edition=True)
    product = random.choice(products)
    cache.set("limited_products", product, time_left)


@shared_task
def process_payment_queue(name="Process payment queue"):
    """обработчик очереди оплаты"""
    jobs = PaymentQueue.objects.all()
    fake_payment_service = FakePaymentService()
    for job in jobs:
        order = job.order
        print(type(order))  # мне ничего не выводит в консоль, не знаю как логировать этот момент
        card_number = job.card_number

        payment_status = fake_payment_service.pay_order(card_number=card_number)

        if payment_status == "success":
            order.status = OrderStatus.objects.get(name="Оплачен")
        else:
            order.status = OrderStatus.objects.get(name="Оплата не выполнена")

        order.save()
        job.delete()

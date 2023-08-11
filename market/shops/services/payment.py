from shops.models import OrderStatusChange, OrderStatus, Order


def update_order_status(order_pk: int, src_pk: int, dst_pk: int) -> None:
    """
    Изменяет статус заказа с сохранением хронологии в модели OrderStatusChange
    :param order_pk: Pk заказа
    :param src_pk: Pk статуса назначения
    :param dst_pk: Pk текущего статуса
    """
    status_srs = OrderStatus.objects.get(pk=src_pk)
    Order.objects.filter(pk=order_pk).update(status=status_srs)
    OrderStatusChange.objects.create(
        order=Order.objects.get(pk=order_pk), src_status=status_srs, dst_status=OrderStatus.objects.get(pk=dst_pk)
    )

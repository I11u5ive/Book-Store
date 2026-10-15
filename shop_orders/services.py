from django.db import transaction

from shop_orders.tasks import send_order_confirmation_email


def send_order_confirmation(order):
    """Schedule confirmation email after the transaction commits."""
    order_id = order.pk

    transaction.on_commit(
        lambda order_id=order_id: send_order_confirmation_email.delay(order_id)
    )
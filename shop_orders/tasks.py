import csv
import logging
from datetime import timedelta
from decimal import Decimal
from io import StringIO

from celery import shared_task
from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.mail import EmailMessage, send_mail
from django.utils import timezone
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_order_confirmation_email(self, order_id):
    """Send an order confirmation asynchronously."""
    from shop_orders.models import Order

    try:
        order = Order.objects.select_related("user").get(pk=order_id)
    except Order.DoesNotExist:
        logger.warning("Order %s no longer exists; email skipped", order_id)
        return "Order not found"

    if not order.user.email:
        logger.info("Order %s has no recipient email", order_id)
        return "No email address"

    lines = [
        f"{item.book.title} x {item.quantity} = {item.subtotal}"
        for item in order.items.select_related("book")
    ]

    message = (
        f"Hello, {order.user.username}!\n\n"
        f"Your order #{order.pk} has been created.\n\n"
        f"{chr(10).join(lines)}\n\n"
        f"Total: {order.total_amount}\n"
    )

    send_mail(
        subject=f"Order #{order.pk} created",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        fail_silently=False,
    )

    logger.info("Confirmation email sent for order %s", order_id)
    return f"Email sent for order {order_id}"


@shared_task
def generate_orders_report():
    """Generate a daily CSV report and email it when a recipient is configured."""
    from shop_orders.models import Order

    now = timezone.now()
    start = now - timedelta(days=1)

    orders = (
        Order.objects.filter(created_at__gte=start, created_at__lt=now)
        .select_related("user")
        .order_by("created_at")
    )

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["Order ID", "Created at", "Username", "Status", "Total amount"]
    )

    count = 0
    total = Decimal("0.00")

    for order in orders:
        writer.writerow(
            [
                order.pk,
                order.created_at.isoformat(),
                order.user.username,
                order.status,
                str(order.total_amount),
            ]
        )
        count += 1
        total += order.total_amount

    csv_content = output.getvalue()
    recipient = getattr(settings, "REPORT_EMAIL", "")

    if recipient:
        email = EmailMessage(
            subject="BookStore daily orders report",
            body=(
                f"Orders in the last 24 hours: {count}\n"
                f"Total order amount: {total}\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        email.attach("orders-report.csv", csv_content, "text/csv")
        email.send(fail_silently=False)
    else:
        logger.info(
            "Report generated but not emailed: REPORT_EMAIL is empty. "
            "Orders=%s total=%s",
            count,
            total,
        )

    return {"orders": count, "total_amount": str(total)}


@shared_task
def clear_expired_sessions():
    """Delete expired Django sessions."""
    Session.objects.clear_expired()
    logger.info("Expired Django sessions cleanup completed")
    return "Expired sessions cleared"


@shared_task
def send_test_email(recipient):
    """Send a simple email to verify the configured email backend."""
    send_mail(
        subject="BookStore Celery test",
        message="Celery successfully sent this test email.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=False,
    )
    return f"Test email sent to {recipient}"

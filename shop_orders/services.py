from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _


def send_order_confirmation(order):
    subject = _("Order confirmation")

    message = _(
        "Your order #%(order_id)s has been created."
    ) % {
        "order_id": order.pk,
    }

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        fail_silently=False,
    )
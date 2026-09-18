from django.utils.translation import gettext_lazy as _
from decimal import Decimal

from django.conf import settings
from django.db import models

from books.models import Book


class Order(models.Model):
    STATUS_CREATED = "created"
    STATUS_PAID = "paid"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_CREATED, _("Created")),
        (STATUS_PAID, _("Paid")),
        (STATUS_CANCELLED, _("Cancelled")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name=_("User"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
        verbose_name=_("Status"),
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Total amount"),
    )

    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_("Stripe session ID"),
    )

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.total_amount is not None:
            self.total_amount = Decimal(str(self.total_amount))

    def save(self, *args, **kwargs):
        self.total_amount = Decimal(str(self.total_amount))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.pk} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Order"),
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name=_("Book"),
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Price"),
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Quantity"),
    )

    class Meta:
        verbose_name = _("Order item")
        verbose_name_plural = _("Order items")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.price is not None:
            self.price = Decimal(str(self.price))

    def save(self, *args, **kwargs):
        self.price = Decimal(str(self.price))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity
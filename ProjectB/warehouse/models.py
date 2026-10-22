from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class StockItem(models.Model):
    book_id = models.PositiveIntegerField(unique=True, db_index=True, verbose_name=_("Book ID in ProjectA"))
    title = models.CharField(max_length=255, verbose_name=_("Book title"))
    quantity = models.PositiveIntegerField(default=0, verbose_name=_("Quantity in warehouse"))
    reserved = models.PositiveIntegerField(default=0, verbose_name=_("Reserved quantity"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Last update"))

    class Meta:
        ordering = ("book_id",)
        verbose_name = _("Stock item")
        verbose_name_plural = _("Stock items")
        permissions = [("manage_stock", "Can manage warehouse stock")]

    @property
    def available_quantity(self):
        return self.quantity - self.reserved

    def clean(self):
        if self.reserved > self.quantity:
            raise ValidationError({"reserved": _("Reserved quantity cannot exceed total quantity.")})

    def __str__(self):
        return f"{self.book_id}: {self.title} ({self.available_quantity} available)"

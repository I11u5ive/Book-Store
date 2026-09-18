from django.utils.translation import gettext_lazy as _
from unicodedata import category
from django.db import models
from decimal import Decimal

# Create your models here.
class Category(models.Model):
    name = models.CharField(
        _("Name"),
        max_length=100,
    )
    slug = models.SlugField(
        _("Slug"),
        unique=True,
    )

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(
        _("Title"),
        max_length=200,
    )

    author = models.CharField(
        _("Author"),
        max_length=200,
    )

    price = models.DecimalField(
        _("Price"),
        max_digits=10,
        decimal_places=2,
    )

    description = models.TextField(
        _("Description"),
    )

    stock = models.PositiveIntegerField(
        _("Stock"),
        default=0,
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="books",
        verbose_name=_("Category"),
    )

    class Meta:
        verbose_name = _("Book")
        verbose_name_plural = _("Books")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.price is not None:
            self.price = Decimal(str(self.price))

    def __str__(self):
        return self.title
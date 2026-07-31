from unicodedata import category

from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Book(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="books"
    )

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    description = models.TextField()

    stock = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title
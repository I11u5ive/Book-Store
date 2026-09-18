from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book

        fields = (
            "title",
            "author",
            "price",
            "description",
            "stock",
            "category",
        )

        labels = {
            "title": _("Title"),
            "author": _("Author"),
            "price": _("Price"),
            "description": _("Description"),
            "stock": _("Stock"),
            "category": _("Category"),
        }

        help_texts = {
            "title": _("Enter the book title."),
            "author": _("Enter the author name."),
            "price": _("Enter the book price."),
            "description": _("Enter the book description."),
            "stock": _("Enter the number of books in stock."),
            "category": _("Select a category."),
        }
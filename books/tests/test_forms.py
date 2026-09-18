import pytest

from books.forms import BookForm
from books.tests.factories import CategoryFactory


pytestmark = pytest.mark.django_db


def test_book_form_valid():
    category = CategoryFactory()

    form = BookForm(
        data={
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "price": "100.00",
            "description": "Fantasy book",
            "stock": 10,
            "category": category.pk,
        }
    )

    assert form.is_valid()


def test_book_form_requires_title():
    category = CategoryFactory()

    form = BookForm(
        data={
            "title": "",
            "author": "Author",
            "price": "100.00",
            "description": "Description",
            "stock": 10,
            "category": category.pk,
        }
    )

    assert not form.is_valid()


def test_book_form_requires_author():
    category = CategoryFactory()

    form = BookForm(
        data={
            "title": "Book",
            "author": "",
            "price": "100.00",
            "description": "Description",
            "stock": 10,
            "category": category.pk,
        }
    )

    assert not form.is_valid()


def test_book_form_requires_price():
    category = CategoryFactory()

    form = BookForm(
        data={
            "title": "Book",
            "author": "Author",
            "price": "",
            "description": "Description",
            "stock": 10,
            "category": category.pk,
        }
    )

    assert not form.is_valid()


def test_book_form_has_category():
    category = CategoryFactory()

    form = BookForm()

    assert form.fields["category"].queryset.filter(
        pk=category.pk
    ).exists()
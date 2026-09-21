from decimal import Decimal

import pytest
from django.db import IntegrityError

from books.models import Book, Category

from .factories import (
    BookFactory,
    CategoryFactory,
)


@pytest.mark.django_db
def test_category_str():
    category = CategoryFactory(
        name="Fantasy"
    )

    assert str(category) == "Fantasy"


@pytest.mark.django_db
def test_category_name():
    category = CategoryFactory(
        name="Science Fiction"
    )

    assert category.name == "Science Fiction"


@pytest.mark.django_db
def test_category_slug():
    category = CategoryFactory(
        slug="science-fiction"
    )

    assert category.slug == "science-fiction"


# Generated with AI, reviewed and modified
@pytest.mark.django_db
def test_category_slug_must_be_unique():
    CategoryFactory(
        slug="fantasy"
    )

    with pytest.raises(IntegrityError):
        CategoryFactory(
            slug="fantasy"
        )


@pytest.mark.django_db
def test_book_str():
    book = BookFactory(
        title="The Hobbit"
    )

    assert str(book) == "The Hobbit"


@pytest.mark.django_db
def test_book_author():
    book = BookFactory(
        author="J.R.R. Tolkien"
    )

    assert book.author == "J.R.R. Tolkien"


@pytest.mark.django_db
def test_book_price():
    book = BookFactory(
        price="150.00"
    )

    assert book.price == Decimal(
        "150.00"
    )


@pytest.mark.django_db
def test_book_stock():
    book = BookFactory(
        stock=20
    )

    assert book.stock == 20


# Generated with AI, reviewed and modified
@pytest.mark.django_db
def test_book_stock_defaults_to_zero():
    category = CategoryFactory()

    book = Book(
        title="New Book",
        author="Test Author",
        price=Decimal("50.00"),
        description="Test description",
        category=category,
    )

    assert book.stock == 0


@pytest.mark.django_db
def test_book_category():
    category = CategoryFactory(
        name="Fantasy"
    )

    book = BookFactory(
        category=category
    )

    assert book.category == category


@pytest.mark.django_db
def test_book_description():
    book = BookFactory(
        description="A great book."
    )

    assert book.description == "A great book."
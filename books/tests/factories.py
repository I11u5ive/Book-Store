from decimal import Decimal

import factory

from books.models import Book, Category


class CategoryFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = Category

    name = factory.Sequence(
        lambda n: f"Category {n}"
    )

    slug = factory.Sequence(
        lambda n: f"category-{n}"
    )


class BookFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = Book

    title = factory.Sequence(
        lambda n: f"Book {n}"
    )

    author = factory.Sequence(
        lambda n: f"Author {n}"
    )

    price = Decimal("100.00")

    description = factory.Faker(
        "paragraph"
    )

    stock = 10

    category = factory.SubFactory(
        CategoryFactory
    )
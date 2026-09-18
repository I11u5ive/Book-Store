import factory

from books.tests.factories import BookFactory
from users.tests.factories import UserFactory

from shop_orders.models import (
    Order,
    OrderItem,
)


class OrderFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = Order

    user = factory.SubFactory(
        UserFactory
    )

    status = Order.STATUS_CREATED

    total_amount = "100.00"


class OrderItemFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(
        OrderFactory
    )

    book = factory.SubFactory(
        BookFactory
    )

    price = factory.LazyAttribute(
        lambda obj: obj.book.price
    )

    quantity = 1
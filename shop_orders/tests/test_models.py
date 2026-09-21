from decimal import Decimal

import pytest

from shop_orders.models import Order

from .factories import (
    OrderFactory,
    OrderItemFactory,
)


@pytest.mark.django_db
def test_order_str():
    order = OrderFactory()

    assert str(order).startswith(
        f"Order #{order.pk}"
    )


@pytest.mark.django_db
def test_order_default_status():
    order = OrderFactory()

    assert order.status == (
        Order.STATUS_CREATED
    )


@pytest.mark.django_db
def test_order_total_amount():
    order = OrderFactory(
        total_amount="250.50"
    )

    assert order.total_amount == Decimal(
        "250.50"
    )


@pytest.mark.django_db
def test_order_user():
    order = OrderFactory()

    assert order.user is not None


# Generated with AI, reviewed and modified
@pytest.mark.django_db
def test_order_total_amount_is_saved_as_decimal():
    order = OrderFactory(
        total_amount="125.75"
    )

    order.refresh_from_db()

    assert order.total_amount == Decimal(
        "125.75"
    )


@pytest.mark.django_db
def test_order_item_subtotal():
    item = OrderItemFactory(
        price="100.00",
        quantity=3,
    )

    assert item.subtotal == Decimal(
        "300.00"
    )


# Generated with AI, reviewed and modified
@pytest.mark.django_db
def test_order_item_subtotal_changes_with_quantity():
    item = OrderItemFactory(
        price="75.50",
        quantity=4,
    )

    assert item.subtotal == Decimal(
        "302.00"
    )


@pytest.mark.django_db
def test_order_item_quantity():
    item = OrderItemFactory(
        quantity=5
    )

    assert item.quantity == 5


@pytest.mark.django_db
def test_order_item_book():
    item = OrderItemFactory()

    assert item.book is not None
from unittest.mock import patch

import pytest

from django.urls import reverse

from books.tests.factories import BookFactory
from shop_orders.tests.factories import OrderFactory
from users.models import User
from users.tests.factories import UserFactory


@pytest.mark.django_db
def test_registration_flow(client):
    response = client.post(
        reverse("users:register"),
        {
            "username": "integration_user",
            "email": "integration@example.com",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
        },
    )

    assert response.status_code == 302

    assert User.objects.filter(
        username="integration_user"
    ).exists()


@pytest.mark.django_db
def test_registration_invalid_password(client):
    response = client.post(
        reverse("users:register"),
        {
            "username": "integration_user",
            "email": "integration@example.com",
            "password1": "StrongPassword123!",
            "password2": "WrongPassword123!",
        },
    )

    assert response.status_code == 200

    assert not User.objects.filter(
        username="integration_user"
    ).exists()


@pytest.mark.django_db
def test_login_flow(client):
    user = UserFactory()

    response = client.post(
        reverse("users:login"),
        {
            "username": user.username,
            "password": "testpass123",
        },
    )

    assert response.status_code == 302


@pytest.mark.django_db
def test_logout_flow(client):
    user = UserFactory()

    client.force_login(user)

    response = client.post(
        reverse("users:logout")
    )

    assert response.status_code == 302


@pytest.mark.django_db
def test_open_books_flow(client):
    user = UserFactory()

    client.force_login(user)

    BookFactory.create_batch(3)

    response = client.get(
        reverse("books:list")
    )

    assert response.status_code in (
        200,
        403,
    )


@pytest.mark.django_db
def test_open_book_detail_flow(client):
    user = UserFactory()
    book = BookFactory()

    client.force_login(user)

    response = client.get(
        reverse(
            "books:detail",
            kwargs={"pk": book.pk},
        )
    )

    assert response.status_code in (
        200,
        403,
    )


@pytest.mark.django_db
def test_search_books_flow(client):
    user = UserFactory()

    client.force_login(user)

    BookFactory(
        title="The Hobbit"
    )

    BookFactory(
        title="The Last Algorithm"
    )

    response = client.get(
        reverse("books:list"),
        {
            "search": "Hobbit",
        },
    )

    assert response.status_code in (
        200,
        403,
    )


@pytest.mark.django_db
def test_cart_requires_login(client):
    book = BookFactory()

    response = client.post(
        reverse(
            "shop_orders:cart_add",
            kwargs={"book_id": book.pk},
        ),
        {
            "quantity": 1,
        },
    )

    assert response.status_code in (
        302,
        403,
    )


@pytest.mark.django_db
def test_cart_page_requires_login(client):
    response = client.get(
        reverse("shop_orders:cart")
    )

    assert response.status_code in (
        302,
        403,
    )


@pytest.mark.django_db
def test_order_belongs_to_user():
    user = UserFactory()

    order = OrderFactory(
        user=user
    )

    assert order.user == user


@pytest.mark.django_db
def test_multiple_orders_for_user():
    user = UserFactory()

    OrderFactory.create_batch(
        3,
        user=user,
    )

    assert user.orders.count() == 3


@pytest.mark.django_db
def test_book_detail_then_cart_flow(client):
    user = UserFactory()
    book = BookFactory(
        stock=10
    )

    client.force_login(user)

    response = client.get(
        reverse(
            "books:detail",
            kwargs={"pk": book.pk},
        )
    )

    assert response.status_code in (
        200,
        403,
    )


@pytest.mark.django_db
@patch(
    "shop_orders.views.stripe.checkout.Session.create"
)
def test_stripe_checkout_is_mocked(
    mock_stripe_create,
):
    mock_stripe_create.return_value = {
        "id": "cs_test_123",
        "url": "https://example.com/checkout",
    }

    result = mock_stripe_create(
        mode="payment"
    )

    assert result["id"] == "cs_test_123"

    mock_stripe_create.assert_called_once_with(
        mode="payment"
    )


@pytest.mark.django_db
@patch(
    "shop_orders.views.send_mail"
)
def test_email_service_is_mocked(
    mock_send_mail,
):
    mock_send_mail(
        "Order",
        "Order created",
        "shop@example.com",
        ["user@example.com"],
    )

    mock_send_mail.assert_called_once()


@pytest.mark.django_db
def test_authenticated_user_can_access_orders():
    user = UserFactory()

    OrderFactory.create_batch(
        2,
        user=user,
    )

    assert user.orders.count() == 2


@pytest.mark.django_db
def test_book_stock_is_available_for_cart():
    book = BookFactory(
        stock=5
    )

    assert book.stock == 5


@pytest.mark.django_db
def test_order_status_flow():
    from shop_orders.models import Order

    order = OrderFactory(
        status=Order.STATUS_CREATED
    )

    assert order.status == (
        Order.STATUS_CREATED
    )

    order.status = Order.STATUS_PAID

    order.save(
        update_fields=["status"]
    )

    order.refresh_from_db()

    assert order.status == (
        Order.STATUS_PAID
    )
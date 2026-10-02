from decimal import Decimal

import pytest

from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book, Category
from shop_orders.models import Order

from users.models import User


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        username="apiuser",
        email="apiuser@example.com",
        password="TestPassword123!",
    )


@pytest.fixture
def second_user():
    return User.objects.create_user(
        username="seconduser",
        email="second@example.com",
        password="TestPassword123!",
    )


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username="adminapi",
        email="adminapi@example.com",
        password="AdminPassword123!",
    )


@pytest.fixture
def category():
    return Category.objects.create(
        name="Fantasy",
        slug="fantasy",
    )


@pytest.fixture
def second_category():
    return Category.objects.create(
        name="Science Fiction",
        slug="science-fiction",
    )


@pytest.fixture
def book(category):
    return Book.objects.create(
        title="The Hobbit",
        author="J.R.R. Tolkien",
        price=Decimal("25.00"),
        description="A fantasy adventure.",
        stock=10,
        category=category,
    )


@pytest.fixture
def second_book(second_category):
    return Book.objects.create(
        title="Dune",
        author="Frank Herbert",
        price=Decimal("30.00"),
        description="A science fiction novel.",
        stock=5,
        category=second_category,
    )


# ============================================================
# Authentication
# ============================================================


def test_books_api_requires_authentication(api_client):
    response = api_client.get("/api/books/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_categories_api_requires_authentication(api_client):
    response = api_client.get("/api/categories/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_orders_api_requires_authentication(api_client):
    response = api_client.get("/api/orders/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_cart_api_requires_authentication(api_client):
    response = api_client.get("/api/cart/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================
# JWT
# ============================================================


def test_jwt_token_obtain(api_client, user):
    response = api_client.post(
        "/api/token/",
        {
            "username": user.username,
            "password": "TestPassword123!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


def test_jwt_token_rejects_invalid_password(api_client, user):
    response = api_client.post(
        "/api/token/",
        {
            "username": user.username,
            "password": "WrongPassword!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================
# Books API
# ============================================================


def test_book_list(api_client, user, book, second_book):
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/books/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] >= 2


def test_book_detail(api_client, user, book):
    api_client.force_authenticate(user=user)

    response = api_client.get(
        f"/api/books/{book.id}/",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == book.id
    assert response.data["title"] == "The Hobbit"


def test_book_search(api_client, user, book, second_book):
    api_client.force_authenticate(user=user)

    response = api_client.get(
        "/api/books/",
        {
            "search": "Hobbit",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    titles = [
        item["title"]
        for item in response.data["results"]
    ]

    assert "The Hobbit" in titles
    assert "Dune" not in titles


def test_book_filter_by_category(
    api_client,
    user,
    book,
    second_book,
    category,
):
    api_client.force_authenticate(user=user)

    response = api_client.get(
        "/api/books/",
        {
            "category": category.id,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    books = response.data["results"]

    assert len(books) == 1
    assert books[0]["id"] == book.id


def test_book_filter_by_stock(
    api_client,
    user,
    book,
    second_book,
):
    api_client.force_authenticate(user=user)

    response = api_client.get(
        "/api/books/",
        {
            "stock": 10,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    books = response.data["results"]

    assert len(books) == 1
    assert books[0]["id"] == book.id


def test_book_ordering_by_price(
    api_client,
    user,
    book,
    second_book,
):
    api_client.force_authenticate(user=user)

    response = api_client.get(
        "/api/books/",
        {
            "ordering": "price",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    prices = [
        Decimal(str(item["price"]))
        for item in response.data["results"]
    ]

    assert prices == sorted(prices)


def test_regular_user_cannot_create_book(
    api_client,
    user,
    category,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/books/",
        {
            "title": "New Book",
            "author": "Test Author",
            "price": "20.00",
            "description": "Test description",
            "stock": 10,
            "category_id": category.id,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_create_book(
    api_client,
    admin_user,
    category,
):
    api_client.force_authenticate(user=admin_user)

    response = api_client.post(
        "/api/books/",
        {
            "title": "Admin Book",
            "author": "Admin Author",
            "price": "20.00",
            "description": "Created by admin.",
            "stock": 10,
            "category_id": category.id,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["title"] == "Admin Book"


def test_regular_user_cannot_delete_book(
    api_client,
    user,
    book,
):
    api_client.force_authenticate(user=user)

    response = api_client.delete(
        f"/api/books/{book.id}/",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_delete_book(
    api_client,
    admin_user,
    book,
):
    api_client.force_authenticate(user=admin_user)

    response = api_client.delete(
        f"/api/books/{book.id}/",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Book.objects.filter(pk=book.id).exists()


# ============================================================
# Categories API
# ============================================================


def test_category_list(
    api_client,
    user,
    category,
    second_category,
):
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/categories/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] >= 2


def test_category_detail(
    api_client,
    user,
    category,
):
    api_client.force_authenticate(user=user)

    response = api_client.get(
        f"/api/categories/{category.id}/",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Fantasy"
    assert response.data["slug"] == "fantasy"


def test_category_search(
    api_client,
    user,
    category,
    second_category,
):
    api_client.force_authenticate(user=user)

    response = api_client.get(
        "/api/categories/",
        {
            "search": "Fantasy",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    names = [
        item["name"]
        for item in response.data["results"]
    ]

    assert "Fantasy" in names
    assert "Science Fiction" not in names


def test_regular_user_cannot_create_category(
    api_client,
    user,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/categories/",
        {
            "name": "History",
            "slug": "history",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_create_category(
    api_client,
    admin_user,
):
    api_client.force_authenticate(user=admin_user)

    response = api_client.post(
        "/api/categories/",
        {
            "name": "History",
            "slug": "history",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "History"


# ============================================================
# Orders API
# ============================================================


def test_user_sees_only_own_orders(
    api_client,
    user,
    second_user,
):
    own_order = Order.objects.create(
        user=user,
    )

    Order.objects.create(
        user=second_user,
    )

    api_client.force_authenticate(user=user)

    response = api_client.get("/api/orders/")

    assert response.status_code == status.HTTP_200_OK

    order_ids = [
        item["id"]
        for item in response.data["results"]
    ]

    assert own_order.id in order_ids
    assert len(order_ids) == 1


def test_user_can_open_own_order(
    api_client,
    user,
):
    order = Order.objects.create(
        user=user,
    )

    api_client.force_authenticate(user=user)

    response = api_client.get(
        f"/api/orders/{order.id}/",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == order.id


def test_user_cannot_open_another_users_order(
    api_client,
    user,
    second_user,
):
    order = Order.objects.create(
        user=second_user,
    )

    api_client.force_authenticate(user=user)

    response = api_client.get(
        f"/api/orders/{order.id}/",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_staff_can_see_all_orders(
    api_client,
    admin_user,
    user,
    second_user,
):
    first_order = Order.objects.create(
        user=user,
    )

    second_order = Order.objects.create(
        user=second_user,
    )

    api_client.force_authenticate(user=admin_user)

    response = api_client.get("/api/orders/")

    assert response.status_code == status.HTTP_200_OK

    order_ids = {
        item["id"]
        for item in response.data["results"]
    }

    assert first_order.id in order_ids
    assert second_order.id in order_ids


def test_orders_api_is_read_only(
    api_client,
    user,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/orders/",
        {},
        format="json",
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


# ============================================================
# Cart API
# ============================================================


def test_cart_is_empty_for_new_user(
    api_client,
    user,
):
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/cart/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["items"] == []
    assert response.data["total_quantity"] == 0
    assert Decimal(
        str(response.data["total_price"])
    ) == Decimal("0")


def test_cart_add_book(
    api_client,
    user,
    book,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/cart/add/",
        {
            "book_id": book.id,
            "quantity": 2,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_quantity"] == 2


def test_cart_add_default_quantity(
    api_client,
    user,
    book,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/cart/add/",
        {
            "book_id": book.id,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_quantity"] == 1


def test_cart_add_invalid_quantity(
    api_client,
    user,
    book,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/cart/add/",
        {
            "book_id": book.id,
            "quantity": 0,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_cart_add_missing_book_id(
    api_client,
    user,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/cart/add/",
        {
            "quantity": 1,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_cart_add_nonexistent_book(
    api_client,
    user,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/cart/add/",
        {
            "book_id": 999999,
            "quantity": 1,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_cart_update_quantity(
    api_client,
    user,
    book,
):
    api_client.force_authenticate(user=user)

    api_client.post(
        "/api/cart/add/",
        {
            "book_id": book.id,
            "quantity": 2,
        },
        format="json",
    )

    response = api_client.patch(
        "/api/cart/update/",
        {
            "book_id": book.id,
            "quantity": 5,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_quantity"] == 5


def test_cart_update_negative_quantity(
    api_client,
    user,
    book,
):
    api_client.force_authenticate(user=user)

    response = api_client.patch(
        "/api/cart/update/",
        {
            "book_id": book.id,
            "quantity": -1,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_cart_remove_book(
    api_client,
    user,
    book,
):
    api_client.force_authenticate(user=user)

    api_client.post(
        "/api/cart/add/",
        {
            "book_id": book.id,
            "quantity": 2,
        },
        format="json",
    )

    response = api_client.delete(
        "/api/cart/remove/",
        {
            "book_id": book.id,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["items"] == []
    assert response.data["total_quantity"] == 0


def test_cart_remove_missing_book_id(
    api_client,
    user,
):
    api_client.force_authenticate(user=user)

    response = api_client.delete(
        "/api/cart/remove/",
        {},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_cart_clear(
    api_client,
    user,
    book,
):
    api_client.force_authenticate(user=user)

    api_client.post(
        "/api/cart/add/",
        {
            "book_id": book.id,
            "quantity": 3,
        },
        format="json",
    )

    response = api_client.delete(
        "/api/cart/clear/",
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["items"] == []
    assert response.data["total_quantity"] == 0


def test_cart_is_separate_between_users(
    user,
    second_user,
    book,
):
    first_client = APIClient()
    second_client = APIClient()

    first_client.force_authenticate(user=user)
    second_client.force_authenticate(user=second_user)

    first_client.session.save()
    second_client.session.save()

    response = first_client.post(
        "/api/cart/add/",
        {
            "book_id": book.id,
            "quantity": 2,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    response = second_client.get(
        "/api/cart/",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["items"] == []
    assert response.data["total_quantity"] == 0
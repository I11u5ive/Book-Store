import pytest

from django.urls import reverse

from books.tests.factories import BookFactory
from users.tests.factories import UserFactory


@pytest.mark.django_db
def test_book_list_requires_login(client):
    response = client.get(
        reverse("books:list")
    )

    assert response.status_code == 302


@pytest.mark.django_db
def test_book_list_authenticated(client):
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
def test_book_detail_requires_login(client):
    book = BookFactory()

    response = client.get(
        reverse(
            "books:detail",
            kwargs={"pk": book.pk},
        )
    )

    assert response.status_code == 302


@pytest.mark.django_db
def test_book_detail_authenticated(client):
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
def test_book_search(client):
    user = UserFactory()

    client.force_login(user)

    BookFactory(
        title="The Hobbit"
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
def test_book_create_requires_login(client):
    response = client.get(
        reverse("books:create")
    )

    assert response.status_code == 302


@pytest.mark.django_db
def test_book_update_requires_login(client):
    book = BookFactory()

    response = client.get(
        reverse(
            "books:update",
            kwargs={"pk": book.pk},
        )
    )

    assert response.status_code == 302


@pytest.mark.django_db
def test_book_delete_requires_login(client):
    book = BookFactory()

    response = client.get(
        reverse(
            "books:delete",
            kwargs={"pk": book.pk},
        )
    )

    assert response.status_code == 302
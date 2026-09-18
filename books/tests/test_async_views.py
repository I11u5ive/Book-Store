import pytest

from django.urls import reverse

from books.tests.factories import BookFactory


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_async_book_count(async_client):
    BookFactory.create_batch(5)

    response = await async_client.get(
        reverse("books:async_count")
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 5


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_async_book_list(async_client):
    BookFactory(
        title="The Hobbit"
    )

    response = await async_client.get(
        reverse("books:async_list")
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["books"]) == 1

    assert data["books"][0]["title"] == (
        "The Hobbit"
    )


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_async_book_search(async_client):
    BookFactory(
        title="The Hobbit"
    )

    BookFactory(
        title="The Last Algorithm"
    )

    response = await async_client.get(
        reverse("books:async_search"),
        {
            "search": "Hobbit",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["books"]) == 1

    assert data["books"][0]["title"] == (
        "The Hobbit"
    )
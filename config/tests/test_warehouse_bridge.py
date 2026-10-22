from unittest.mock import Mock

import pytest
import requests
from rest_framework.test import APIClient

from books.tests.factories import BookFactory
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_authenticated_user_can_read_warehouse_stock(monkeypatch, settings):
    book = BookFactory()
    user = get_user_model().objects.create_user(username="reader", password="SafeTestPass123!")
    response = Mock(status_code=200)
    response.json.return_value = {"book_id": book.pk, "title": book.title, "quantity": 7}
    mocked_get = Mock(return_value=response)
    monkeypatch.setattr("config.warehouse_bridge.requests.get", mocked_get)

    client = APIClient()
    client.force_authenticate(user=user)
    result = client.get(f"/api/warehouse/books/{book.pk}/")

    assert result.status_code == 200
    assert result.data["quantity"] == 7
    mocked_get.assert_called_once()
    assert mocked_get.call_args.kwargs["timeout"] == 3


@pytest.mark.django_db
def test_warehouse_timeout_returns_gateway_timeout(monkeypatch):
    book = BookFactory()
    user = get_user_model().objects.create_user(username="reader2", password="SafeTestPass123!")
    monkeypatch.setattr("config.warehouse_bridge.requests.get", Mock(side_effect=requests.Timeout))

    client = APIClient()
    client.force_authenticate(user=user)
    result = client.get(f"/api/warehouse/books/{book.pk}/")

    assert result.status_code == 504
    assert "timed out" in result.data["detail"].lower()


@pytest.mark.django_db
def test_staff_can_sync_book_to_warehouse(monkeypatch):
    book = BookFactory()
    staff = get_user_model().objects.create_superuser(username="warehouse-sync-admin", password="SafeTestPass123!", email="sync@example.com")
    response = Mock(status_code=201)
    response.json.return_value = {"book_id": book.pk, "title": book.title, "quantity": book.stock}
    mocked_post = Mock(return_value=response)
    monkeypatch.setattr("config.warehouse_bridge.requests.post", mocked_post)

    client = APIClient()
    client.force_authenticate(user=staff)
    result = client.post(f"/api/warehouse/sync/{book.pk}/")

    assert result.status_code == 201
    assert result.data["book_id"] == book.pk
    assert mocked_post.call_args.kwargs["json"]["quantity"] == book.stock

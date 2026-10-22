import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from warehouse.models import StockItem
from warehouse.tasks import generate_stock_report


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def regular_user(db):
    return get_user_model().objects.create_user(username="reader", password="SafeTestPass123!")


@pytest.fixture
def admin_user(db):
    return get_user_model().objects.create_superuser(username="manager", password="SafeTestPass123!", email="manager@example.com")


@pytest.fixture
def user_client(regular_user):
    client = APIClient()
    client.force_authenticate(user=regular_user)
    return client


@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


def service_client(settings):
    client = APIClient()
    client.credentials(HTTP_X_SERVICE_TOKEN=settings.WAREHOUSE_SERVICE_TOKEN)
    return client


@pytest.mark.django_db
def test_unauthenticated_stock_request_is_rejected():
    response = APIClient().get("/api/stock/")
    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_authenticated_user_can_list_and_retrieve_stock(user_client):
    item = StockItem.objects.create(book_id=12, title="Django Basics", quantity=9, reserved=2)
    result = user_client.get("/api/stock/")
    assert result.status_code == 200
    assert len(result.data) == 1
    detail = user_client.get(f"/api/stock/{item.book_id}/")
    assert detail.status_code == 200
    assert detail.data["available_quantity"] == 7


@pytest.mark.django_db
def test_regular_user_cannot_write_stock(user_client):
    result = user_client.post("/api/stock/", {"book_id": 5, "title": "No permission", "quantity": 3}, format="json")
    assert result.status_code == 403


@pytest.mark.django_db
def test_staff_can_create_update_delete_stock(admin_client):
    created = admin_client.post("/api/stock/", {"book_id": 21, "title": "Python", "quantity": 8, "reserved": 1}, format="json")
    assert created.status_code == 201
    cached_detail = admin_client.get("/api/stock/21/")
    assert cached_detail.status_code == 200
    updated = admin_client.patch("/api/stock/21/", {"quantity": 10}, format="json")
    assert updated.status_code == 200
    assert updated.data["available_quantity"] == 9
    deleted = admin_client.delete("/api/stock/21/")
    assert deleted.status_code == 204
    assert not StockItem.objects.filter(book_id=21).exists()


@pytest.mark.django_db
def test_serializer_rejects_reserved_quantity_above_total(admin_client):
    result = admin_client.post("/api/stock/", {"book_id": 22, "title": "Invalid", "quantity": 2, "reserved": 5}, format="json")
    assert result.status_code == 400


@pytest.mark.django_db
def test_service_token_can_sync_create_update_and_list(settings):
    client = service_client(settings)
    created = client.post("/api/stock/sync/", {"book_id": 33, "title": "Synced title", "quantity": 14}, format="json")
    assert created.status_code == 201
    updated = client.post("/api/stock/sync/", {"book_id": 33, "title": "Updated title", "quantity": 18}, format="json")
    assert updated.status_code == 200
    listed = client.get("/api/stock/")
    assert listed.status_code == 200
    assert listed.data[0]["quantity"] == 18


@pytest.mark.django_db
def test_service_sync_cannot_reduce_quantity_below_reserved(settings):
    StockItem.objects.create(book_id=34, title="Reserved", quantity=10, reserved=8)
    client = service_client(settings)
    result = client.post("/api/stock/sync/", {"book_id": 34, "title": "Reserved", "quantity": 4}, format="json")
    assert result.status_code == 409


@pytest.mark.django_db
def test_wrong_service_token_is_rejected(settings):
    client = APIClient()
    client.credentials(HTTP_X_SERVICE_TOKEN="wrong-token")
    result = client.post("/api/stock/sync/", {"book_id": 35, "title": "Unauthorized", "quantity": 1}, format="json")
    assert result.status_code in (401, 403)


@pytest.mark.django_db
def test_report_endpoint_and_celery_task(user_client):
    StockItem.objects.create(book_id=41, title="A", quantity=10, reserved=2)
    StockItem.objects.create(book_id=42, title="B", quantity=3, reserved=0)
    response = user_client.get("/api/report/")
    assert response.status_code == 200
    assert response.data["total_books"] == 2
    assert response.data["total_available"] == 11
    task_result = generate_stock_report.run()
    assert task_result["total_reserved"] == 2
    assert task_result["low_stock_items"] == 1


@pytest.mark.django_db
def test_cache_is_invalidated_after_stock_write(admin_client, user_client):
    assert user_client.get("/api/stock/").data == []
    admin_client.post("/api/stock/", {"book_id": 50, "title": "New book", "quantity": 6}, format="json")
    result = user_client.get("/api/stock/")
    assert len(result.data) == 1
    assert result.data[0]["book_id"] == 50


@pytest.mark.django_db
def test_health_endpoint_is_public():
    result = APIClient().get("/api/health/")
    assert result.status_code == 200
    assert result.data == {"status": "ok", "service": "ProjectB"}


@pytest.mark.django_db
def test_setup_command_creates_warehouse_manager_group(admin_user):
    call_command("setup_warehouse", verbosity=0)
    group = Group.objects.get(name="WarehouseManagers")
    assert group.permissions.filter(codename="manage_stock").exists()


@pytest.mark.django_db
def test_warehouse_manager_group_can_create_stock(admin_user):
    call_command("setup_warehouse", verbosity=0)
    manager = get_user_model().objects.create_user(username="warehouse-operator", password="SafeTestPass123!")
    manager.groups.add(Group.objects.get(name="WarehouseManagers"))
    client = APIClient()
    client.force_authenticate(user=manager)
    result = client.post("/api/stock/", {"book_id": 60, "title": "Group permission", "quantity": 4}, format="json")
    assert result.status_code == 201

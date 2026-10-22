import hmac

from django.conf import settings
from rest_framework.permissions import BasePermission, SAFE_METHODS


def is_service_request(request):
    expected = getattr(settings, "WAREHOUSE_SERVICE_TOKEN", "")
    supplied = request.headers.get("X-Service-Token", "")
    return bool(expected and supplied and hmac.compare_digest(expected, supplied))


class IsAuthenticatedOrService(BasePermission):
    """Permit JWT-authenticated users or the internal ProjectA service token."""

    def has_permission(self, request, view):
        return is_service_request(request) or bool(request.user and request.user.is_authenticated)


class CanManageStock(BasePermission):
    """Allow only staff, a permission-bearing user/group, or ProjectA's service token to write stock."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if is_service_request(request):
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser:
            return True
        if user.has_perm("warehouse.manage_stock"):
            return True
        permission_by_method = {
            "POST": "warehouse.add_stockitem",
            "PUT": "warehouse.change_stockitem",
            "PATCH": "warehouse.change_stockitem",
            "DELETE": "warehouse.delete_stockitem",
        }
        required_permission = permission_by_method.get(request.method)
        return bool(required_permission and user.has_perm(required_permission))


class HasWarehouseServiceToken(BasePermission):
    """Restrict service-to-service endpoints to the shared internal token."""

    def has_permission(self, request, view):
        return is_service_request(request)

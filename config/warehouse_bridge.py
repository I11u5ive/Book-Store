import logging

import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema

from books.models import Book

logger = logging.getLogger(__name__)


def _headers():
    token = settings.WAREHOUSE_SERVICE_TOKEN
    if not token:
        logger.error("WAREHOUSE_SERVICE_TOKEN is not configured")
        return None
    return {"X-Service-Token": token, "Accept": "application/json"}


def _decode_response(upstream_response):
    try:
        payload = upstream_response.json()
    except ValueError:
        logger.error("Warehouse service returned invalid JSON (status=%s)", upstream_response.status_code)
        return Response({"detail": "Warehouse service returned an invalid response."}, status=status.HTTP_502_BAD_GATEWAY)
    upstream_status = upstream_response.status_code
    if upstream_status >= 500:
        logger.error("Warehouse service failed with HTTP %s", upstream_status)
        return Response({"detail": "Warehouse service failed."}, status=status.HTTP_502_BAD_GATEWAY)
    return Response(payload, status=upstream_status)


class WarehouseBookStockView(APIView):
    """Read a book's warehouse stock by calling ProjectB's internal API."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses=OpenApiTypes.OBJECT, tags=["warehouse"])
    def get(self, request, book_id):
        headers = _headers()
        if headers is None:
            return Response({"detail": "Warehouse integration is not configured."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        url = f"{settings.WAREHOUSE_API_URL.rstrip('/')}/{book_id}/"
        try:
            upstream_response = requests.get(url, headers=headers, timeout=3)
        except requests.Timeout:
            logger.warning("Timeout while reading warehouse stock for book_id=%s", book_id, exc_info=True)
            return Response({"detail": "Warehouse service timed out."}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except requests.RequestException:
            logger.exception("Unable to reach warehouse service for book_id=%s", book_id)
            return Response({"detail": "Warehouse service is temporarily unavailable."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        logger.info("Warehouse stock lookup completed for book_id=%s status=%s", book_id, upstream_response.status_code)
        return _decode_response(upstream_response)


class WarehouseBookSyncView(APIView):
    """Synchronize one BookStore book into ProjectB; staff-only endpoint."""

    permission_classes = [IsAdminUser]

    @extend_schema(request=None, responses=OpenApiTypes.OBJECT, tags=["warehouse"])
    def post(self, request, book_id):
        book = get_object_or_404(Book, pk=book_id)
        headers = _headers()
        if headers is None:
            return Response({"detail": "Warehouse integration is not configured."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        payload = {"book_id": book.pk, "title": book.title, "quantity": book.stock}
        url = f"{settings.WAREHOUSE_API_URL.rstrip('/')}/sync/"
        try:
            upstream_response = requests.post(url, json=payload, headers=headers, timeout=3)
        except requests.Timeout:
            logger.warning("Timeout while syncing book_id=%s to warehouse", book_id, exc_info=True)
            return Response({"detail": "Warehouse service timed out."}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except requests.RequestException:
            logger.exception("Unable to sync book_id=%s to warehouse", book_id)
            return Response({"detail": "Warehouse service is temporarily unavailable."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        logger.info("Warehouse sync completed for book_id=%s status=%s", book_id, upstream_response.status_code)
        return _decode_response(upstream_response)

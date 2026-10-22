import logging

from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema

from .models import StockItem
from .permissions import CanManageStock, HasWarehouseServiceToken, IsAuthenticatedOrService
from .serializers import StockItemSerializer, StockSyncSerializer
from .services import build_stock_report

logger = logging.getLogger(__name__)


class StockListCreateView(generics.ListCreateAPIView):
    """List cached stock or create a stock item with sufficient permissions."""

    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer
    permission_classes = [IsAuthenticatedOrService]

    def get_permissions(self):
        permissions = [IsAuthenticatedOrService()]
        if self.request.method not in ("GET", "HEAD", "OPTIONS"):
            permissions.append(CanManageStock())
        return permissions

    def get(self, request, *args, **kwargs):
        cache_key = "warehouse:stock:list:v1"
        data = cache.get(cache_key)
        if data is None:
            data = self.get_serializer(self.get_queryset(), many=True).data
            cache.set(cache_key, data, timeout=60)
            logger.info("Warehouse stock list loaded from database")
        else:
            logger.info("Warehouse stock list served from cache")
        return Response(data)

    def perform_create(self, serializer):
        item = serializer.save()
        logger.info("Stock item created book_id=%s by user=%s", item.book_id, self.request.user)


class StockDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a stock item identified by ProjectA's book ID."""

    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer
    lookup_field = "book_id"
    lookup_url_kwarg = "book_id"
    permission_classes = [IsAuthenticatedOrService]

    def get_permissions(self):
        permissions = [IsAuthenticatedOrService()]
        if self.request.method not in ("GET", "HEAD", "OPTIONS"):
            permissions.append(CanManageStock())
        return permissions

    def retrieve(self, request, *args, **kwargs):
        book_id = kwargs[self.lookup_url_kwarg]
        cache_key = f"warehouse:stock:detail:v1:{book_id}"
        cached = cache.get(cache_key)
        if cached is not None:
            logger.info("Warehouse stock detail served from cache book_id=%s", book_id)
            return Response(cached)
        instance = self.get_object()
        data = self.get_serializer(instance).data
        cache.set(cache_key, data, timeout=60)
        logger.info("Warehouse stock detail loaded from database book_id=%s", book_id)
        return Response(data)

    def perform_update(self, serializer):
        item = serializer.save()
        logger.info("Stock item updated book_id=%s by user=%s", item.book_id, self.request.user)

    def perform_destroy(self, instance):
        book_id = instance.book_id
        instance.delete()
        logger.info("Stock item deleted book_id=%s by user=%s", book_id, self.request.user)


class StockSyncView(APIView):
    """Internal upsert endpoint used only by ProjectA's service token."""

    permission_classes = [HasWarehouseServiceToken]

    @extend_schema(
        request=StockSyncSerializer,
        responses={201: StockItemSerializer, 200: StockItemSerializer, 400: OpenApiTypes.OBJECT, 409: OpenApiTypes.OBJECT},
        tags=["warehouse"],
    )
    def post(self, request):
        incoming = StockSyncSerializer(data=request.data)
        if not incoming.is_valid():
            logger.warning("Invalid warehouse sync payload: %s", incoming.errors)
            return Response(incoming.errors, status=status.HTTP_400_BAD_REQUEST)

        values = incoming.validated_data
        item = StockItem.objects.filter(book_id=values["book_id"]).first()
        if item and values["quantity"] < item.reserved:
            return Response(
                {"detail": "Quantity cannot be lower than already reserved stock."},
                status=status.HTTP_409_CONFLICT,
            )
        created = item is None
        if created:
            item = StockItem.objects.create(**values)
        else:
            item.title = values["title"]
            item.quantity = values["quantity"]
            item.save(update_fields=("title", "quantity", "updated_at"))
        logger.info("ProjectA synchronized book_id=%s created=%s", item.book_id, created)
        return Response(StockItemSerializer(item).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class StockReportView(APIView):
    """Return cached high-level warehouse analytics."""

    permission_classes = [IsAuthenticatedOrService]

    @extend_schema(responses=OpenApiTypes.OBJECT, tags=["analytics"])
    def get(self, request):
        report = cache.get("warehouse:report:v1")
        if report is None:
            report = build_stock_report()
            cache.set("warehouse:report:v1", report, timeout=60)
        return Response(report)


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(responses=OpenApiTypes.OBJECT, tags=["health"])
    def get(self, request):
        return Response({"status": "ok", "service": "ProjectB"})

from django.urls import path

from .warehouse_bridge import WarehouseBookStockView, WarehouseBookSyncView

app_name = "warehouse_bridge"
urlpatterns = [
    path("books/<int:book_id>/", WarehouseBookStockView.as_view(), name="book-stock"),
    path("sync/<int:book_id>/", WarehouseBookSyncView.as_view(), name="book-sync"),
]

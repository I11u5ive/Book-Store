from django.urls import path

from .views import HealthView, StockDetailView, StockListCreateView, StockReportView, StockSyncView

app_name = "warehouse"
urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("stock/sync/", StockSyncView.as_view(), name="stock-sync"),
    path("stock/", StockListCreateView.as_view(), name="stock-list"),
    path("stock/<int:book_id>/", StockDetailView.as_view(), name="stock-detail"),
    path("report/", StockReportView.as_view(), name="stock-report"),
]

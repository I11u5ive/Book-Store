from django.contrib import admin

from .models import StockItem


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ("book_id", "title", "quantity", "reserved", "available_quantity", "updated_at")
    search_fields = ("title", "book_id")
    list_filter = ("updated_at",)
    readonly_fields = ("updated_at",)

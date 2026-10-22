from django.db.models import Sum

from .models import StockItem


def build_stock_report():
    totals = StockItem.objects.aggregate(total_quantity=Sum("quantity"), total_reserved=Sum("reserved"))
    total_quantity = totals["total_quantity"] or 0
    total_reserved = totals["total_reserved"] or 0
    return {
        "total_books": StockItem.objects.count(),
        "total_quantity": total_quantity,
        "total_reserved": total_reserved,
        "total_available": total_quantity - total_reserved,
        "low_stock_items": sum(1 for item in StockItem.objects.all() if item.available_quantity < 5),
    }

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import StockItem


@receiver(post_save, sender=StockItem)
@receiver(post_delete, sender=StockItem)
def invalidate_stock_cache(sender, instance, **kwargs):
    cache.delete("warehouse:stock:list:v1")
    cache.delete("warehouse:report:v1")
    cache.delete(f"warehouse:stock:detail:v1:{instance.book_id}")

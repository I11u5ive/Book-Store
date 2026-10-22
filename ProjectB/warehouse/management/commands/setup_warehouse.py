from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from warehouse.models import StockItem


class Command(BaseCommand):
    help = "Create the WarehouseManagers group and assign stock permissions."

    def handle(self, *args, **options):
        content_type = ContentType.objects.get_for_model(StockItem)
        codenames = ("view_stockitem", "add_stockitem", "change_stockitem", "delete_stockitem", "manage_stock")
        permissions = Permission.objects.filter(content_type=content_type, codename__in=codenames)
        group, created = Group.objects.get_or_create(name="WarehouseManagers")
        group.permissions.set(permissions)
        action = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f"WarehouseManagers group {action}; {permissions.count()} permissions assigned."))

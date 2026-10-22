from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="StockItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("book_id", models.PositiveIntegerField(db_index=True, unique=True, verbose_name="Book ID in ProjectA")),
                ("title", models.CharField(max_length=255, verbose_name="Book title")),
                ("quantity", models.PositiveIntegerField(default=0, verbose_name="Quantity in warehouse")),
                ("reserved", models.PositiveIntegerField(default=0, verbose_name="Reserved quantity")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Last update")),
            ],
            options={
                "verbose_name": _("Stock item"),
                "verbose_name_plural": _("Stock items"),
                "ordering": ("book_id",),
                "permissions": [("manage_stock", "Can manage warehouse stock")],
            },
        ),
    ]

from rest_framework import serializers

from .models import StockItem


class StockItemSerializer(serializers.ModelSerializer):
    available_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = StockItem
        fields = ("id", "book_id", "title", "quantity", "reserved", "available_quantity", "updated_at")
        read_only_fields = ("id", "updated_at", "available_quantity")

    def validate(self, attrs):
        quantity = attrs.get("quantity", getattr(self.instance, "quantity", 0))
        reserved = attrs.get("reserved", getattr(self.instance, "reserved", 0))
        if reserved > quantity:
            raise serializers.ValidationError({"reserved": "Reserved quantity cannot exceed total quantity."})
        if self.instance and "book_id" in attrs and attrs["book_id"] != self.instance.book_id:
            raise serializers.ValidationError({"book_id": "Book ID cannot be changed after synchronization."})
        return attrs


class StockSyncSerializer(serializers.Serializer):
    book_id = serializers.IntegerField(min_value=1)
    title = serializers.CharField(max_length=255)
    quantity = serializers.IntegerField(min_value=0)

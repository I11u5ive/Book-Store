from decimal import Decimal

from rest_framework import serializers

from books.models import Book, Category
from shop_orders.models import Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for book categories.
    """

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
        ]


class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for books with nested category data.
    """

    category = CategorySerializer(
        read_only=True,
    )

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
    )

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "price",
            "description",
            "stock",
            "category",
            "category_id",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for order items with nested book data.
    """

    book = BookSerializer(
        read_only=True,
    )

    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        source="book",
        write_only=True,
    )

    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "book",
            "book_id",
            "price",
            "quantity",
            "subtotal",
        ]

    def get_subtotal(self, obj) -> Decimal:
        """
        Return the calculated subtotal for the order item.
        """
        return obj.subtotal


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for orders with nested order items.
    """

    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "username",
            "created_at",
            "status",
            "total_amount",
            "stripe_session_id",
            "items",
        ]
        read_only_fields = [
            "user",
            "created_at",
            "total_amount",
            "stripe_session_id",
        ]


class CartItemSerializer(serializers.Serializer):
    """
    Serializer for a session-based cart item.
    """

    book = BookSerializer(
        read_only=True,
    )

    quantity = serializers.IntegerField()

    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )


class CartSerializer(serializers.Serializer):
    """
    Serializer for the complete session-based cart.
    """

    items = CartItemSerializer(
        many=True,
    )

    total_quantity = serializers.IntegerField()

    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )


class CartBookSerializer(serializers.Serializer):
    """
    Request serializer for cart operations that target a book.
    """

    book_id = serializers.IntegerField()


class CartAddSerializer(CartBookSerializer):
    """
    Request serializer for adding a book to the cart.
    """

    quantity = serializers.IntegerField(
        required=False,
        default=1,
        min_value=1,
    )


class CartUpdateSerializer(CartBookSerializer):
    """
    Request serializer for updating a cart item quantity.
    """

    quantity = serializers.IntegerField(
        min_value=0,
    )
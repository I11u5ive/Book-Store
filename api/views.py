import logging

from django.shortcuts import get_object_or_404

from rest_framework import (
    filters,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
)

from books.models import Book, Category
from shop_orders.cart import Cart
from shop_orders.models import Order

from .permissions import IsOwnerOrReadOnly
from .serializers import (
    BookSerializer,
    CartAddSerializer,
    CartBookSerializer,
    CartSerializer,
    CartUpdateSerializer,
    CategorySerializer,
    OrderSerializer,
)


logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for book categories.

    Authenticated users can view categories.
    Only administrators can create, update or delete categories.
    """

    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "name",
        "slug",
    ]

    search_fields = [
        "name",
        "slug",
    ]

    ordering_fields = [
        "id",
        "name",
        "slug",
    ]

    ordering = [
        "name",
    ]

    def get_permissions(self):
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            return [
                IsAdminUser(),
            ]

        return [
            IsAuthenticated(),
        ]


class BookViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for books.

    Authenticated users can view books.
    Only administrators can create, update or delete books.
    """

    queryset = (
        Book.objects
        .select_related("category")
        .all()
        .order_by("title")
    )

    serializer_class = BookSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "category",
        "stock",
    ]

    search_fields = [
        "title",
        "author",
        "description",
    ]

    ordering_fields = [
        "id",
        "title",
        "author",
        "price",
        "stock",
    ]

    ordering = [
        "title",
    ]

    def get_permissions(self):
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            return [
                IsAdminUser(),
            ]

        return [
            IsAuthenticated(),
        ]


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API ViewSet for orders.

    Regular users can see only their own orders.
    Staff users can see all orders.

    Order creation remains part of the existing checkout flow,
    which handles stock locking, order items, Stripe and email.
    """

    serializer_class = OrderSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "status",
    ]

    search_fields = [
        "status",
        "user__username",
    ]

    ordering_fields = [
        "id",
        "created_at",
        "total_amount",
        "status",
    ]

    ordering = [
        "-created_at",
    ]

    permission_classes = [
        IsAuthenticated,
        IsOwnerOrReadOnly,
    ]

    def get_queryset(self):
        """
        Return all orders for staff and only owned orders
        for regular users.
        """

        if getattr(
            self,
            "swagger_fake_view",
            False,
        ):
            return Order.objects.none()

        queryset = (
            Order.objects
            .select_related("user")
            .prefetch_related(
                "items__book__category",
            )
            .order_by("-created_at")
        )

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(
            user=self.request.user,
        )


class CartViewSet(viewsets.ViewSet):
    """
    API ViewSet for modifying the session-based shopping cart.

    The cart is stored in the user's Django session
    and therefore is not represented by a database model.
    """

    serializer_class = CartSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_cart(self, request):
        """
        Build and return the current user's cart response.
        """

        cart = Cart(request)

        items = list(cart)

        serializer = CartSerializer(
            {
                "items": items,
                "total_quantity": len(cart),
                "total_price": cart.get_total_price(),
            }
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(
                response=CartSerializer,
                description="Current user's shopping cart.",
            ),
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="",
        url_name="list",
    )
    def cart(self, request):
        """
        Return the current user's shopping cart.
        """

        return self.get_cart(request)

    @extend_schema(
        request=CartAddSerializer,
        responses={
            200: OpenApiResponse(
                response=CartSerializer,
                description="Updated shopping cart.",
            ),
            400: OpenApiResponse(
                description="Invalid cart item data.",
            ),
            404: OpenApiResponse(
                description="Book not found.",
            ),
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="add",
    )
    def add(self, request):
        """
        Add a book to the shopping cart.
        """

        book_id = request.data.get("book_id")
        quantity = request.data.get(
            "quantity",
            1,
        )

        if book_id is None:
            return Response(
                {
                    "detail": "book_id is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            book_id = int(book_id)
            quantity = int(quantity)
        except (
            TypeError,
            ValueError,
        ):
            return Response(
                {
                    "detail": (
                        "book_id and quantity "
                        "must be integers."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity <= 0:
            return Response(
                {
                    "detail": (
                        "quantity must be greater "
                        "than zero."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        book = get_object_or_404(
            Book,
            pk=book_id,
        )

        cart = Cart(request)

        cart.add(
            book,
            quantity=quantity,
        )

        return self.get_cart(request)

    @extend_schema(
        request=CartUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=CartSerializer,
                description="Updated shopping cart.",
            ),
            400: OpenApiResponse(
                description="Invalid cart item data.",
            ),
            404: OpenApiResponse(
                description="Book not found.",
            ),
        },
    )
    @action(
        detail=False,
        methods=["patch"],
        url_path="update",
    )
    def update_item(self, request):
        """
        Set the exact quantity of a book in the cart.
        """

        book_id = request.data.get("book_id")
        quantity = request.data.get("quantity")

        if (
            book_id is None
            or quantity is None
        ):
            return Response(
                {
                    "detail": (
                        "book_id and quantity "
                        "are required."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            book_id = int(book_id)
            quantity = int(quantity)
        except (
            TypeError,
            ValueError,
        ):
            return Response(
                {
                    "detail": (
                        "book_id and quantity "
                        "must be integers."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity < 0:
            return Response(
                {
                    "detail": (
                        "quantity cannot be negative."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        book = get_object_or_404(
            Book,
            pk=book_id,
        )

        cart = Cart(request)

        cart.add(
            book,
            quantity=quantity,
            override_quantity=True,
        )

        return self.get_cart(request)

    @extend_schema(
        request=CartBookSerializer,
        responses={
            200: OpenApiResponse(
                response=CartSerializer,
                description="Updated shopping cart.",
            ),
            400: OpenApiResponse(
                description="Invalid book ID.",
            ),
            404: OpenApiResponse(
                description="Book not found.",
            ),
        },
    )
    @action(
        detail=False,
        methods=["delete"],
        url_path="remove",
    )
    def remove(self, request):
        """
        Remove a book from the shopping cart.
        """

        book_id = request.data.get("book_id")

        if book_id is None:
            return Response(
                {
                    "detail": "book_id is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            book_id = int(book_id)
        except (
            TypeError,
            ValueError,
        ):
            return Response(
                {
                    "detail": (
                        "book_id must be an integer."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        book = get_object_or_404(
            Book,
            pk=book_id,
        )

        cart = Cart(request)

        cart.remove(book)

        return self.get_cart(request)

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=CartSerializer,
                description="Empty shopping cart.",
            ),
        },
    )
    @action(
        detail=False,
        methods=["delete"],
        url_path="clear",
    )
    def clear(self, request):
        """
        Remove all books from the shopping cart.
        """

        cart = Cart(request)

        cart.clear()

        serializer = CartSerializer(
            {
                "items": [],
                "total_quantity": 0,
                "total_price": cart.get_total_price(),
            }
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class CartView(APIView):
    """
    API endpoint for retrieving the current user's
    shopping cart.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=CartSerializer,
                description="Current user's shopping cart.",
            ),
        },
    )
    def get(self, request):
        """
        Return the current user's cart.
        """

        cart = Cart(request)

        items = list(cart)

        serializer = CartSerializer(
            {
                "items": items,
                "total_quantity": len(cart),
                "total_price": cart.get_total_price(),
            }
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
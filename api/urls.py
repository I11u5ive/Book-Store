from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import (
    BookViewSet,
    CartView,
    CartViewSet,
    CategoryViewSet,
    OrderViewSet,
)


router = DefaultRouter()


router.register(
    "books",
    BookViewSet,
    basename="book",
)


router.register(
    "categories",
    CategoryViewSet,
    basename="category",
)


router.register(
    "orders",
    OrderViewSet,
    basename="order",
)


router.register(
    "cart",
    CartViewSet,
    basename="cart",
)


urlpatterns = [
    path(
        "cart/",
        CartView.as_view(),
        name="cart",
    ),
] + router.urls
from django.urls import path

from . import views


app_name = "shop_orders"


urlpatterns = [
    path(
        "",
        views.cart_detail,
        name="cart_detail",
    ),

    path(
        "",
        views.cart_detail,
        name="cart",
    ),

    path(
        "add/<int:book_id>/",
        views.cart_add,
        name="cart_add",
    ),

    path(
        "",
        views.cart_detail,
        name="cart_detail",
    ),

    path(
        "add/<int:book_id>/",
        views.cart_add,
        name="cart_add",
    ),

    path(
        "update/<int:book_id>/",
        views.cart_update,
        name="cart_update",
    ),

    path(
        "remove/<int:book_id>/",
        views.cart_remove,
        name="cart_remove",
    ),

    path(
        "clear/",
        views.cart_clear,
        name="cart_clear",
    ),

    path(
        "checkout/",
        views.checkout,
        name="checkout",
    ),

    path(
        "success/",
        views.checkout_success,
        name="success",
    ),

    path(
        "cancel/",
        views.checkout_cancel,
        name="cancel",
    ),
]
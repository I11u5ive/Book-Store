from django.contrib import admin
from django.urls import include, path
from debug_toolbar.toolbar import debug_toolbar_urls


urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "books/",
        include("books.urls"),
    ),

    path(
        "accounts/",
        include("users.urls"),
    ),
    path(
        "cart/",
        include("shop_orders.urls"),
    ),
] + debug_toolbar_urls()
from django.contrib import admin
from django.urls import include, path
from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf.urls.i18n import i18n_patterns


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
    path("i18n/",
         include("django.conf.urls.i18n")),
] + debug_toolbar_urls()
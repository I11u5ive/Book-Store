from django.urls import path

from .views import (
    BookCreateView,
    BookDeleteView,
    BookDetailView,
    BookListView,
    BookUpdateView,
)

from .async_views import (
    async_book_count,
    async_book_list,
    async_book_search,
)


app_name = "books"


urlpatterns = [
    path(
        "",
        BookListView.as_view(),
        name="list",
    ),

    path(
        "create/",
        BookCreateView.as_view(),
        name="create",
    ),

    path(
        "<int:pk>/",
        BookDetailView.as_view(),
        name="detail",
    ),

    path(
        "<int:pk>/edit/",
        BookUpdateView.as_view(),
        name="update",
    ),

    path(
        "<int:pk>/delete/",
        BookDeleteView.as_view(),
        name="delete",
    ),

    path(
        "async/count/",
        async_book_count,
        name="async_count",
    ),

    path(
        "async/list/",
        async_book_list,
        name="async_list",
    ),

    path(
        "async/search/",
        async_book_search,
        name="async_search",
    ),
]
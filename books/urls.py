from django.urls import path

from .views import (
    BookListView,
    BookDetailView,
    BookCreateView,
    BookUpdateView,
    BookDeleteView,
)


app_name = "books"


urlpatterns = [
    path(
        "",
        BookListView.as_view(),
        name="list"
    ),

    path(
        "<int:pk>/",
        BookDetailView.as_view(),
        name="detail"
    ),

    path(
        "create/",
        BookCreateView.as_view(),
        name="create"
    ),

    path(
        "<int:pk>/update/",
        BookUpdateView.as_view(),
        name="update"
    ),

    path(
        "<int:pk>/delete/",
        BookDeleteView.as_view(),
        name="delete"
    ),
]
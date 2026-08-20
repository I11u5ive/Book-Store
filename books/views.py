import logging
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .models import Book
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin

logger = logging.getLogger(__name__)


class BookListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ListView
):

    model = Book

    template_name = "books/book_list.html"

    context_object_name = "books"

    paginate_by = 6

    permission_required = "books.view_book"

    def get_queryset(self):

        logger.info(
            "Book list requested by user: %s",
            self.request.user
        )

        queryset = Book.objects.all()

        search = self.request.GET.get("search")

        if search:

            logger.info(
                "Book search: %s",
                search
            )

            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(author__icontains=search)
            )

        return queryset


class BookDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DetailView
):

    model = Book

    template_name = "books/book_detail.html"

    context_object_name = "book"

    permission_required = "books.view_book"


class BookCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView
):

    model = Book

    template_name = "books/book_form.html"

    fields = [
        "title",
        "author",
        "price",
        "description",
        "stock",
        "category",
    ]

    permission_required = "books.add_book"

    success_url = reverse_lazy("books:list")


class BookUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView
):

    model = Book

    template_name = "books/book_form.html"

    fields = [
        "title",
        "author",
        "price",
        "description",
        "stock",
        "category",
    ]

    permission_required = "books.change_book"

    success_url = reverse_lazy("books:list")


class BookDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DeleteView
):

    model = Book

    template_name = "books/book_confirm_delete.html"

    permission_required = "books.delete_book"

    success_url = reverse_lazy("books:list")
import logging

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import BookForm
from .models import Book


logger = logging.getLogger(__name__)


class BookListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    model = Book
    template_name = "books/book_list.html"
    context_object_name = "books"
    paginate_by = 6
    permission_required = "books.view_book"

    def get_queryset(self):
        queryset = Book.objects.select_related("category")

        search = self.request.GET.get("search", "").strip()

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(author__icontains=search)
            )

        logger.info(
            "Book list requested by user=%s search=%s",
            self.request.user,
            search,
        )

        return queryset


class BookDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DetailView,
):
    model = Book
    template_name = "books/book_detail.html"
    context_object_name = "book"
    permission_required = "books.view_book"

    def get_queryset(self):
        return Book.objects.select_related("category")


class BookCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView,
):
    model = Book
    form_class = BookForm
    template_name = "books/book_form.html"
    success_url = reverse_lazy("books:list")
    permission_required = "books.add_book"


class BookUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView,
):
    model = Book
    form_class = BookForm
    template_name = "books/book_form.html"
    success_url = reverse_lazy("books:list")
    permission_required = "books.change_book"


class BookDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DeleteView,
):
    model = Book
    template_name = "books/book_confirm_delete.html"
    success_url = reverse_lazy("books:list")
    permission_required = "books.delete_book"
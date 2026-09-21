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
    """Display a paginated list of books with optional title/author search."""

    model = Book
    template_name = "books/book_list.html"
    context_object_name = "books"
    paginate_by = 6
    permission_required = "books.view_book"

    def get_queryset(self):
        """Return books with related categories and optional search filtering."""
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
    """Display detailed information about a single book."""

    model = Book
    template_name = "books/book_detail.html"
    context_object_name = "book"
    permission_required = "books.view_book"

    def get_queryset(self):
        """Return books with their related category loaded efficiently."""
        return Book.objects.select_related("category")


class BookCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView,
):
    """Create a new book when the user has the required permission."""

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
    """Update an existing book when the user has the required permission."""

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
    """Delete an existing book when the user has the required permission."""

    model = Book
    template_name = "books/book_confirm_delete.html"
    success_url = reverse_lazy("books:list")
    permission_required = "books.delete_book"
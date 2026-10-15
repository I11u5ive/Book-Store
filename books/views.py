
import logging

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.cache import cache
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
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


@method_decorator(
    cache_page(60 * 5, key_prefix="books_list_v1"),
    name="dispatch",
)
@method_decorator(vary_on_cookie, name="dispatch")
class BookListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Display a cached, paginated list of books."""
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
                Q(title__icontains=search) | Q(author__icontains=search)
            )

        logger.info(
            "Book list requested by user=%s search=%s",
            self.request.user,
            search,
        )
        return queryset


class BookDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Display book details using the low-level Redis cache."""
    model = Book
    template_name = "books/book_detail.html"
    context_object_name = "book"
    permission_required = "books.view_book"

    def get_object(self, queryset=None):
        book_id = self.kwargs.get(self.pk_url_kwarg)
        key = f"books:detail:v1:{book_id}"

        book = cache.get(key)
        if book is None:
            book = (
                Book.objects.select_related("category")
                .filter(pk=book_id)
                .first()
            )
            if book is None:
                from django.http import Http404
                raise Http404("Book not found")
            cache.set(key, book, timeout=300)

        return book


class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = "books/book_form.html"
    success_url = reverse_lazy("books:list")
    permission_required = "books.add_book"


class BookUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = "books/book_form.html"
    success_url = reverse_lazy("books:list")
    permission_required = "books.change_book"


class BookDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Book
    template_name = "books/book_confirm_delete.html"
    success_url = reverse_lazy("books:list")
    permission_required = "books.delete_book"

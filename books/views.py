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


class BookListView(ListView):
    model = Book
    template_name = "books/book_list.html"
    context_object_name = "books"
    paginate_by = 6

    def get_queryset(self):
        queryset = Book.objects.all()

        search = self.request.GET.get("search")
        category = self.request.GET.get("category")

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(author__icontains=search)
            )

        if category:
            queryset = queryset.filter(
                category__slug=category
            )

        return queryset


class BookDetailView(DetailView):
    model = Book
    template_name = "books/book_detail.html"
    context_object_name = "book"


class BookCreateView(CreateView):
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

    success_url = reverse_lazy("books:list")


class BookUpdateView(UpdateView):
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

    success_url = reverse_lazy("books:list")


class BookDeleteView(DeleteView):
    model = Book
    template_name = "books/book_confirm_delete.html"

    success_url = reverse_lazy("books:list")
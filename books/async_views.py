from django.db.models import Q
from django.http import JsonResponse

from .models import Book


async def async_book_count(request):
    """Return the total number of books as JSON."""
    count = await Book.objects.acount()
    return JsonResponse({"count": count})


async def async_book_list(request):
    """Return all books as a JSON list ordered by title."""
    books = []

    async for book in Book.objects.all().order_by("title"):
        books.append(
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "price": str(book.price),
                "stock": book.stock,
            }
        )

    return JsonResponse({"books": books})


async def async_book_search(request):
    """Return books matching the optional title or author search."""
    search = request.GET.get("search", "").strip()

    queryset = Book.objects.all()

    if search:
        queryset = queryset.filter(
            Q(title__icontains=search)
            | Q(author__icontains=search)
        )

    books = []

    async for book in queryset.order_by("title"):
        books.append(
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "price": str(book.price),
            }
        )

    return JsonResponse(
        {
            "search": search,
            "books": books,
        }
    )
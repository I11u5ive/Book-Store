from django.conf import settings
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from .models import Book, Category

BOOK_LIST_CACHE_KEY = "books:list:v1"
BOOK_LIST_PAGE_CACHE_PATTERN = "*cache_page.books_list_v1*"
BOOK_DETAIL_CACHE_KEY = "books:detail:v1:{book_id}"


def invalidate_book_fragment_cache(book_id):
    """
    Delete cached book-card fragments for all configured languages.
    """
    languages = {settings.LANGUAGE_CODE}

    languages.update(language_code for language_code, _ in settings.LANGUAGES)

    for language_code in languages:
        key = make_template_fragment_key(
            "book_card",
            [book_id, language_code],
        )
        cache.delete(key)


def invalidate_book_cache(book_id=None):
    """
    Invalidate book-list, book-card and optional book-detail caches.
    """
    cache.delete(BOOK_LIST_CACHE_KEY)
    cache.delete_pattern(BOOK_LIST_PAGE_CACHE_PATTERN)

    if book_id is not None:
        cache.delete(BOOK_DETAIL_CACHE_KEY.format(book_id=book_id))
        invalidate_book_fragment_cache(book_id)


@receiver(post_save, sender=Book)
@receiver(post_delete, sender=Book)
def invalidate_book_after_change(sender, instance, **kwargs):
    invalidate_book_cache(instance.pk)


@receiver(pre_delete, sender=Category)
def invalidate_books_before_category_delete(sender, instance, **kwargs):
    """
    Invalidate related books before deleting their category.
    """
    book_ids = list(
        Book.objects.filter(category_id=instance.pk).values_list("pk", flat=True)
    )

    invalidate_book_cache()

    for book_id in book_ids:
        invalidate_book_cache(book_id)


@receiver(post_save, sender=Category)
def invalidate_books_after_category_save(sender, instance, **kwargs):
    """
    Category names appear on book cards and in cached book details.
    """
    invalidate_book_cache()

    book_ids = Book.objects.filter(category_id=instance.pk).values_list("pk", flat=True)

    for book_id in book_ids:
        invalidate_book_cache(book_id)


@receiver(post_delete, sender=Category)
def invalidate_books_after_category_delete(sender, instance, **kwargs):
    invalidate_book_cache()

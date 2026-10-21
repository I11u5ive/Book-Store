import pytest

from django.conf import settings
from django.core.cache.utils import make_template_fragment_key

from django.core.cache import cache

from books.tests.factories import BookFactory


@pytest.mark.django_db
def test_book_save_invalidates_detail_cache():
    book = BookFactory()
    key = f"books:detail:v1:{book.pk}"

    cache.set(key, "cached book", timeout=300)
    assert cache.get(key) == "cached book"

    book.title = "Updated title"
    book.save()

    assert cache.get(key) is None


@pytest.mark.django_db
def test_book_delete_invalidates_detail_cache():
    book = BookFactory()
    key = f"books:detail:v1:{book.pk}"

    cache.set(key, "cached book", timeout=300)
    assert cache.get(key) == "cached book"

    book.delete()

    assert cache.get(key) is None


@pytest.mark.django_db
def test_book_save_invalidates_list_page_cache():
    book = BookFactory()

    # Simulate a cached response created by cache_page.
    key = "views.decorators.cache.cache_page." "books_list_v1.GET.test-cache-key"
    cache.set(key, "cached list", timeout=300)
    assert cache.get(key) == "cached list"

    book.title = "Updated title"
    book.save()

    assert cache.get(key) is None

    @pytest.mark.django_db
    def test_book_save_invalidates_card_fragment_cache():
        book = BookFactory()
        language_code = settings.LANGUAGE_CODE

        key = make_template_fragment_key(
            "book_card",
            [book.pk, language_code],
        )

        cache.set(key, "cached card", timeout=300)
        assert cache.get(key) == "cached card"

        book.price = "199.00"
        book.save()

        assert cache.get(key) is None

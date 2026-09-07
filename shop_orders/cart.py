from decimal import Decimal

from books.models import Book


CART_SESSION_ID = "cart"


class Cart:

    def __init__(self, request):
        self.session = request.session

        cart = self.session.get(CART_SESSION_ID)

        if cart is None:
            cart = self.session[CART_SESSION_ID] = {}

        self.cart = cart

    def add(
        self,
        book,
        quantity=1,
        override_quantity=False,
    ):
        book_id = str(book.id)

        if book_id not in self.cart:
            self.cart[book_id] = {
                "quantity": 0,
            }

        if override_quantity:
            self.cart[book_id]["quantity"] = quantity
        else:
            self.cart[book_id]["quantity"] += quantity

        if self.cart[book_id]["quantity"] <= 0:
            self.remove(book)
            return

        self.save()

    def remove(self, book):
        book_id = str(book.id)

        if book_id in self.cart:
            del self.cart[book_id]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session.pop(CART_SESSION_ID, None)
        self.session.modified = True

    def __len__(self):
        return sum(
            item["quantity"]
            for item in self.cart.values()
        )

    def __iter__(self):
        book_ids = self.cart.keys()

        books = Book.objects.filter(
            id__in=book_ids,
        )

        books_by_id = {
            str(book.id): book
            for book in books
        }

        for book_id, cart_item in self.cart.items():

            book = books_by_id.get(book_id)

            if book is None:
                continue

            quantity = cart_item["quantity"]

            yield {
                "book": book,
                "quantity": quantity,
                "price": book.price,
                "total_price": book.price * quantity,
            }

    def get_total_price(self):
        return sum(
            (
                item["total_price"]
                for item in self
            ),
            Decimal("0.00"),
        )
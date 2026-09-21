# AI Code Review

## 1. Overview

This document describes the AI-assisted code review performed for the Django BookStore project.

The purpose of the review was to identify potential improvements in:

* code structure;
* maintainability;
* separation of responsibilities;
* database query efficiency;
* validation;
* authentication and permissions;
* testing;
* documentation;
* service-layer usage.

The reviewed files were:

* `books/views.py`
* `shop_orders/views.py`
* `shop_orders/cart.py`
* `shop_orders/services.py`
* `users/tests/factories.py`

The recommendations were reviewed manually and tested before being accepted.

---

## 2. Current Project Quality

Before the review, the project already had several good practices:

* Django Class-Based Views are used for book CRUD operations.
* Authentication is protected with `LoginRequiredMixin`.
* Object permissions are protected with `PermissionRequiredMixin`.
* `Q` objects are used for book searching.
* `select_related("category")` is used to optimize category loading.
* Shopping cart logic is separated into a dedicated `Cart` class.
* Database transactions are used during checkout.
* `transaction.on_commit()` is used for post-transaction email processing.
* Automated tests cover models, forms, views, integration scenarios, and async views.
* The project uses PostgreSQL in Docker.
* Async Django ORM operations are used in the asynchronous book views.

The initial test suite contained 53 tests.

---

# 3. Review of `books/views.py`

## Finding 1 — Missing delete permission declaration

### Location

`books/views.py`

`BookDeleteView`

### Observation

The view inherits from:

```python
PermissionRequiredMixin
```

but originally did not explicitly define:

```python
permission_required = "books.delete_book"
```

Other CRUD views already defined their required permissions:

```text
BookListView    → books.view_book
BookCreateView  → books.add_book
BookUpdateView  → books.change_book
BookDeleteView  → missing
```

### Recommendation

Add:

```python
permission_required = "books.delete_book"
```

to `BookDeleteView`.

### Decision

**Accepted.**

### Implementation

The final implementation is:

```python
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
```

### Reason

This makes permission handling consistent across all CRUD views and explicitly protects the delete operation with the corresponding Django model permission.

### Verification

The full test suite was executed after the change.

Result:

```text
53 passed
```

Therefore, the change did not break the existing functionality.

---

# 4. Review of `BookListView`

## Finding 2 — Efficient related-object loading

### Observation

`BookListView.get_queryset()` uses:

```python
Book.objects.select_related("category")
```

This is appropriate because `Book` has a related `Category` object and the category is used by the book templates.

### Recommendation

Keep the current implementation.

### Decision

**Accepted — no code change required.**

### Reason

`select_related()` allows the related category to be loaded together with the book query instead of potentially causing additional database queries.

The existing implementation is already appropriate for this use case.

---

## Finding 3 — Search implementation

### Observation

The book list supports searching by both title and author:

```python
queryset = queryset.filter(
    Q(title__icontains=search)
    | Q(author__icontains=search)
)
```

### Recommendation

Keep the current implementation.

### Decision

**Accepted — no code change required.**

### Reason

The use of `Q` objects provides a clear and idiomatic Django implementation for an OR-based search condition.

The search parameter is also stripped before being used:

```python
search = self.request.GET.get("search", "").strip()
```

This avoids unnecessary filtering for leading/trailing whitespace.

---

# 5. Review of `shop_orders/views.py`

## Finding 4 — `checkout()` contains too many responsibilities

### Location

`shop_orders/views.py`

### Observation

The `ch

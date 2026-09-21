# AI Prompts

## 1. Purpose

This document contains the prompts used during AI-assisted development and code review of the Django BookStore project.

The prompts were used for:

* code review;
* identification of architectural improvements;
* security and permission review;
* database query review;
* test generation;
* test coverage analysis;
* documentation review;
* evaluation of suggested changes.

AI-generated recommendations were reviewed manually before being applied to the project.

---

# 2. AI Code Review Prompt — Book Views

## Prompt

```text
Review the Django views in books/views.py.

Focus on:

1. Code quality and readability.
2. Django best practices.
3. Class-Based Views usage.
4. Authentication and authorization.
5. PermissionRequiredMixin configuration.
6. Database query efficiency.
7. Use of select_related and ORM queries.
8. Search implementation using Q objects.
9. Error handling.
10. Missing docstrings.
11. Potential security problems.
12. Maintainability.

Identify concrete problems rather than suggesting unnecessary refactoring.

For every finding provide:

- file and location;
- problem description;
- why it matters;
- recommended improvement;
- priority;
- whether the change is necessary or optional.

Do not rewrite the entire file unless a change is required.
```

## Purpose

This prompt was used to review:

```text
books/views.py
```

The review identified the missing explicit delete permission:

```python
permission_required = "books.delete_book"
```

The recommendation was accepted and implemented.

---

# 3. AI Code Review Prompt — Shopping Cart and Checkout

## Prompt

```text
Review the Django shopping cart and checkout implementation.

Analyze:

- shop_orders/views.py
- shop_orders/cart.py
- shop_orders/services.py

Focus on:

1. Separation of responsibilities.
2. Service layer design.
3. Database transactions.
4. select_for_update usage.
5. Stock validation.
6. Order and OrderItem creation.
7. Stripe Checkout integration.
8. Email sending.
9. Session-based cart handling.
10. Duplicate business logic.
11. Error handling.
12. Security.
13. Testability.
14. Maintainability.
15. Database query efficiency.

Pay special attention to checkout() and determine whether it contains too many responsibilities.

Identify duplicated functionality between views.py and services.py.

For each finding provide:

- file;
- function or class;
- problem;
- recommendation;
- priority;
- expected benefit;
- risk of changing the code.

Do not recommend large architectural changes unless they are justified by the existing code.
```

## Purpose

This prompt identified that `checkout()` performs several responsibilities:

* reading the cart;
* creating the order;
* validating stock;
* creating order items;
* calculating the total;
* creating Stripe line items;
* creating the Stripe Checkout session;
* saving the Stripe session ID;
* sending order email after commit;
* clearing the cart.

The review recommended moving business logic into the service layer.

This recommendation was accepted as a refactoring target.

---

# 4. AI Code Review Prompt — Shopping Cart

## Prompt

```text
Review shop_orders/cart.py as an isolated component.

Determine whether the Cart class has a clear responsibility.

Check:

- session handling;
- add/update/remove operations;
- quantity handling;
- clearing the cart;
- iteration over books;
- database queries;
- total price calculation;
- handling of deleted books;
- Decimal arithmetic;
- possible edge cases;
- testability.

Identify actual problems and avoid unnecessary abstractions.

For every finding explain whether the code should be changed or kept as-is.
```

## Purpose

The review confirmed that the `Cart` class has a reasonably clear responsibility.

The current implementation:

* stores cart data in the session;
* loads books in a single query using `id__in`;
* maps books by ID;
* calculates item totals using `Decimal`;
* handles missing books safely during iteration.

No immediate major refactoring was required.

---

# 5. AI Code Review Prompt — Service Layer

## Prompt

```text
Review shop_orders/services.py together with shop_orders/views.py.

Look for duplicated business logic and determine whether the service layer is actually being used.

Compare:

- send_order_confirmation(order)
- send_order_email(order_id)

Determine whether these functions represent overlapping responsibilities.

Recommend a clean way to consolidate order confirmation email functionality without changing observable application behaviour.

Consider:

- transaction boundaries;
- transaction.on_commit();
- email delivery;
- testability;
- dependency on the Order model;
- user email availability.

Do not remove functionality merely to make the code shorter.
```

## Purpose

The review identified two separate order-email implementations.

The recommendation was to consolidate the functionality in the service layer.

This was accepted as a refactoring target.

---

# 6. AI Prompt — Authentication and Permissions Review

## Prompt

```text
Review authentication and authorization in this Django project.

Check:

- LoginRequiredMixin
- PermissionRequiredMixin
- @login_required
- @require_POST
- model permissions
- book CRUD permissions
- cart modification permissions
- checkout access

Verify that each protected operation has an appropriate authentication and permission requirement.

Pay special attention to whether PermissionRequiredMixin has permission_required configured correctly.

Identify missing or inconsistent permissions.

Do not change permissions unless the required permission is clear from the existing application structure.
```

## Purpose

This review helped identify the missing permission declaration in `BookDeleteView`.

The final CRUD permission structure is:

```text
BookListView    → books.view_book
BookCreateView  → books.add_book
BookUpdateView  → books.change_book
BookDeleteView  → books.delete_book
```

---

# 7. AI Prompt — Database and ORM Review

## Prompt

```text
Review the Django ORM usage in the provided project.

Focus on:

- select_related;
- prefetch_related;
- Q objects;
- queryset filtering;
- N+1 query risks;
- transaction.atomic;
- select_for_update;
- unnecessary database queries;
- Decimal calculations;
- concurrent stock updates.

Review the code in the context of a small Django bookstore application.

For each potential optimization explain:

1. What the current code does.
2. What problem could occur.
3. Whether an optimization is actually necessary.
4. What the safest change would be.

Avoid premature optimization.
```

## Purpose

The review confirmed several existing good practices:

```python
Book.objects.select_related("category")
```

for related category loading, and:

```python
Book.objects.select_for_update().get(...)
```

during checkout stock validation.

The current transaction handling was considered appropriate and was kept.

---

# 8. AI Prompt — Test Generation

## Prompt

```text
Generate pytest tests for the Django BookStore project.

The tests should cover the most important behaviour of the provided models.

Focus on:

- valid model creation;
- required fields;
- Decimal price handling;
- stock values;
- relationships;
- calculated properties;
- order totals;
- order item subtotals;
- model string representations;
- edge cases.

Use pytest and pytest-django.

Use the existing project factories where possible.

Do not modify production code just to make tests pass.

Generated tests must be readable and independent.

Every generated test file should contain the comment:

# Generated with AI, reviewed and modified

After generating the tests, explain what each test verifies and identify any assumptions that should be checked manually.
```

## Purpose

This prompt was used to assist with generating and reviewing tests for the project's models.

The generated tests were then manually checked and modified where necessary.

In particular, DecimalField values were verified using appropriate `Decimal` semantics rather than relying on incorrect assumptions about Python numeric types.

---

# 9. AI Prompt — View Test Generation

## Prompt

```text
Generate pytest tests for the Django BookStore views.

Use pytest-django and the existing factories.

Cover:

- authenticated users;
- unauthenticated users;
- permission checks;
- book list;
- book detail;
- book search;
- pagination;
- CRUD permissions;
- redirects;
- invalid requests where appropriate.

Do not assume that every authenticated user has every permission.

Use reverse() instead of hard-coded URLs where possible.

Keep tests independent and readable.

Add:

# Generated with AI, reviewed and modified

to the generated test file.

After generating the tests, explain which cases are covered and identify cases that should be manually verified.
```

## Purpose

This prompt was used for test coverage of book views and integration scenarios.

The resulting tests contributed to the current test suite of 53 passing tests.

---

# 10. AI Prompt — Async View Testing

## Prompt

```text
Review the async Django views and their pytest tests.

The project uses Django async views and async ORM operations.

Check:

- async def views;
- async ORM usage;
- async iteration;
- AsyncClient;
- sync_to_async;
- database isolation;
- pytest-django configuration;
- pytest-asyncio configuration.

Identify possible problems with asynchronous database access and test database cleanup.

Do not change working async production code unless a concrete problem is demonstrated.

If a test database warning occurs, distinguish between a test failure and a teardown warning.
```

## Purpose

This prompt was used to review:

```text
books/async_views.py
books/tests/test_async_views.py
```

The async tests were configured with transactional database access.

The tests currently pass, although one PostgreSQL test database teardown warning remains.

---

# 11. AI Prompt — Coverage Analysis

## Prompt

```text
Analyze the pytest coverage report for the Django BookStore project.

Identify:

1. Overall coverage percentage.
2. Files with low coverage.
3. Business-critical code with insufficient coverage.
4. Missing tests that would provide the most value.
5. Areas where additional tests would be unnecessary.

The assignment requires at least 60% coverage.

Do not recommend tests solely to increase the percentage. Prioritize meaningful application behaviour.
```

## Purpose

The coverage analysis showed:

```text
836 statements
151 missed
82% coverage
```

The project therefore exceeds the required 60% coverage.

The analysis identified `shop_orders/services.py`, `shop_orders/cart.py`, and parts of `shop_orders/views.py` as areas where additional meaningful tests could improve confidence.

---

# 12. AI Prompt — Docstring Review

## Prompt

```text
Review all Django view functions and Class-Based Views in the project.

Check whether each view has a useful docstring.

A good docstring should describe the purpose of the view rather than simply repeat its class or function name.

Identify missing or low-quality docstrings.

Provide concise replacement docstrings where necessary.

Do not add unnecessary documentation to trivial code.
```

## Purpose

The review was used to verify documentation of the project's views.

The book CBVs contain descriptive docstrings explaining their responsibilities.

---

# 13. AI Prompt — Warning Investigation

## Prompt

```text
Analyze the following pytest warning:

PytestWarning:
Error when trying to teardown test databases:
OperationalError(
    'database "test_bookstore" is being accessed by other users'
)

The warning occurs after an async Django test using PostgreSQL.

Determine possible causes related to:

- pytest-django;
- pytest-asyncio;
- Django async ORM;
- database connections;
- connection cleanup;
- transaction management.

Distinguish between a functional test failure and a teardown warning.

Do not recommend suppressing the warning without understanding the underlying cause.
```

## Purpose

This prompt was used to investigate the remaining PostgreSQL test teardown warning.

The warning does not currently cause test failure:

```text
53 passed
```

It remains a separate investigation item.

---

# 14. AI Prompt — Safe Refactoring Review

## Prompt

```text
Before applying any proposed refactoring to the Django BookStore project, evaluate it for behavioural changes.

For the proposed change:

1. Explain what code behaviour changes.
2. Identify tests that could be affected.
3. Identify hidden dependencies.
4. Determine whether the change is safe.
5. Suggest the smallest implementation that achieves the desired improvement.
6. Explain how the change should be verified.

Do not recommend a refactoring simply because it reduces the number of lines of code.
Preserve existing application behaviour.
```

## Purpose

This prompt establishes the principle used throughout the review:

> A refactoring is acceptable only if its benefits justify its complexity and existing behaviour is preserved.

---

# 15. Example of AI Recommendation Rejected After Testing

One AI recommendation was to resolve the `factory_boy` deprecation warning by adding:

```python
skip_postgeneration_save = True
```

to `UserFactory.Meta`.

The change looked reasonable based on the warning message, but it was tested before being accepted.

After applying it, the test suite changed from:

```text
53 passed
```

to:

```text
8 failed, 45 passed
```

The failures affected authentication and integration tests.

The change was therefore reverted.

This demonstrates the workflow used for AI-assisted development:

```text
AI recommendation
        ↓
Human review
        ↓
Implementation
        ↓
Automated tests
        ↓
Unexpected behaviour detected
        ↓
Change rejected/reverted
```

The warning remains documented rather than being "fixed" by a change that breaks existing behaviour.

---

# 16. AI-Assisted Development Workflow

The general workflow used for this project was:

```text
1. Identify a development task
        ↓
2. Ask AI for analysis
        ↓
3. Review AI recommendations
        ↓
4. Select relevant recommendations
        ↓
5. Implement the smallest justified change
        ↓
6. Run automated tests
        ↓
7. Inspect failures and warnings
        ↓
8. Revert unsafe changes
        ↓
9. Measure coverage
        ↓
10. Document the final decisions
```

AI was used as a development and review assistant rather than as an automatic source of unverified code.

---

# 17. Final Verification

The current project test suite was verified with:

```bash
docker compose exec web pytest -q
```

Current result:

```text
53 passed, 21 warnings
```

Coverage was measured with:

```bash
docker compose exec web pytest --cov=. --cov-report=term-missing -q
```

Current total coverage:

```text
82%
```

The project therefore satisfies the required minimum coverage of 60%.

---

# 18. Conclusion

AI was used throughout the development process to:

* review existing code;
* identify potential improvements;
* analyze architecture;
* generate and review tests;
* inspect database usage;
* review authentication and permissions;
* review documentation;
* analyze test coverage;
* investigate warnings.

All significant AI recommendations were manually reviewed.

Recommendations were either:

* accepted and implemented;
* accepted as future refactoring targets;
* deferred because they were not sufficiently valuable;
* or rejected after testing demonstrated an undesirable behavioural change.

This approach ensures that AI assistance improves the project while the final implementation remains under developer control.

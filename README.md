# BookStore

Django-based online bookstore with PostgreSQL, Redis, authentication, shopping cart, orders, Stripe Checkout integration, asynchronous views, tests, and AI-assisted development.

## Project Features

* Django web application for an online bookstore
* Book and category management
* Custom Django User model
* User registration, login, and logout
* Authentication and permission-based access control
* Class-based views for book CRUD operations
* Book search by title and author
* Pagination
* Shopping cart
* Order creation
* Stripe Checkout integration
* Order confirmation email
* PostgreSQL database
* Redis service
* Docker Compose environment
* Asynchronous Django views
* Automated tests with pytest
* Code coverage analysis
* Django Debug Toolbar
* Request logging middleware
* Internationalization support

## Technologies

* Python
* Django
* PostgreSQL
* Redis
* Docker
* Docker Compose
* pytest
* pytest-django
* pytest-asyncio
* factory_boy
* Stripe API
* Bootstrap

## Running the Project

Build and start the containers:

```bash
docker compose up --build
```

The application is available on:

```text
http://localhost:8000/
```

To stop the containers:

```bash
docker compose down
```

To stop the containers and remove volumes:

```bash
docker compose down -v
```

## Running Tests

Run the complete test suite:

```bash
docker compose exec web pytest
```

Run tests with coverage:

```bash
docker compose exec web pytest --cov=. --cov-report=term-missing -q
```

The project should maintain at least 60% code coverage as required by the coursework.

## Database

The project uses PostgreSQL when running through Docker Compose.

Django database configuration is provided through environment variables stored in `.env`.

Database migrations are applied automatically by the Docker entrypoint when the application container starts.

## AI Usage

Artificial intelligence was used as a development and code-review assistant during the implementation of this project.

AI was used for:

* Reviewing Django views and identifying potential improvements.
* Reviewing authentication and permission handling.
* Reviewing Django ORM queries and database access.
* Reviewing the shopping cart and checkout implementation.
* Identifying opportunities for refactoring.
* Generating and improving automated tests.
* Reviewing asynchronous Django views and async tests.
* Analysing test coverage.
* Checking and improving view docstrings.
* Investigating pytest and factory_boy warnings.
* Preparing documentation for the development process.

### AI Code Review

The following areas were reviewed with AI assistance:

* `books/views.py`
* `shop_orders/views.py`
* `shop_orders/cart.py`
* `shop_orders/services.py`
* authentication and permission-related code
* database and ORM usage
* asynchronous views and tests

The AI review identified several possible improvements.

One concrete improvement was applied to `BookDeleteView`: the view originally did not explicitly define the required delete permission. The following permission was added:

```python
permission_required = "books.delete_book"
```

The existing `select_related("category")` optimization and `Q`-based search were reviewed and retained because they were appropriate for the current implementation.

The checkout code was also reviewed as a possible refactoring target because the `checkout()` view contains several responsibilities, including order creation, stock validation, Stripe session preparation, email scheduling, and cart handling.

### AI Recommendations That Were Tested and Rejected

AI was also used to investigate a factory_boy deprecation warning.

A recommendation was tested to add:

```python
skip_postgeneration_save = True
```

to `UserFactory`.

The change was not kept because it caused authentication-related tests to fail. The existing `UserFactory` uses a post-generation password operation, and the tests depend on the resulting user instance being saved.

After reverting the change, the complete test suite returned to:

```text
53 passed
```

Therefore, the warning was documented rather than fixed through a change that would reduce the correctness of the test suite.

### Testing and Verification

AI-generated or AI-assisted tests were reviewed and executed against the project.

The final test suite currently passes:

```text
53 passed
```

Coverage was also checked with pytest-cov. The measured project coverage was:

```text
82%
```

which is above the required 60% threshold.

An asynchronous PostgreSQL test-database teardown warning was also observed during testing. It was documented as a test-environment warning rather than treated as an application failure because the tests themselves completed successfully.

### Human Review

AI suggestions were not applied automatically.

Each proposed change was reviewed and tested against the existing project. Changes that improved the code without breaking existing functionality were retained, while changes that caused regressions were reverted.

The AI interaction history and prompts used during the development process are documented in:

* `AI_REVIEW.md`
* `AI_PROMPTS.md`

## Project Structure

```text
BookStore/
├── books/
├── users/
├── shop_orders/
├── config/
├── locale/
├── Dockerfile
├── docker-compose.yml
├── docker-entrypoint.sh
├── manage.py
├── pytest.ini
├── requirements.txt
├── .env
├── AI_REVIEW.md
├── AI_PROMPTS.md
└── README.md
```

## Development Notes

The project is developed and tested inside the Docker Compose environment.

After changing Python source files, rebuild the application image when necessary:

```bash
docker compose up -d --build
```

Check running containers with:

```bash
docker compose ps
```

View application logs with:

```bash
docker compose logs web
```

View database logs with:

```bash
docker compose logs db
```

from decimal import Decimal

import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.urls import reverse
from django.views.decorators.http import require_POST

from books.models import Book

from .cart import Cart
from .models import Order, OrderItem


@login_required
def cart_detail(request):
    """Display the current user's shopping cart."""

    cart = Cart(request)

    return render(
        request,
        "shop_orders/cart_detail.html",
        {
            "cart": cart,
        },
    )


@login_required
@require_POST
def cart_add(request, book_id):
    """Add the requested quantity of a book to the shopping cart."""

    book = get_object_or_404(
        Book,
        id=book_id,
    )

    try:
        quantity = int(
            request.POST.get(
                "quantity",
                1,
            )
        )
    except ValueError:
        return HttpResponseBadRequest(
            "Invalid quantity"
        )

    if quantity < 1:
        return HttpResponseBadRequest(
            "Quantity must be at least 1"
        )

    if quantity > book.stock:
        messages.error(
            request,
            f"Only {book.stock} copies available.",
        )

        return redirect(
            "shop_orders:cart_detail"
        )

    cart = Cart(request)

    cart.add(
        book=book,
        quantity=quantity,
    )

    messages.success(
        request,
        f'"{book.title}" added to cart.',
    )

    return redirect(
        "shop_orders:cart_detail"
    )


@login_required
@require_POST
def cart_update(request, book_id):
    """Update or remove a book quantity in the shopping cart."""

    book = get_object_or_404(
        Book,
        id=book_id,
    )

    try:
        quantity = int(
            request.POST.get(
                "quantity",
                1,
            )
        )
    except ValueError:
        return HttpResponseBadRequest(
            "Invalid quantity"
        )

    cart = Cart(request)

    if quantity <= 0:
        cart.remove(book)

    elif quantity > book.stock:
        messages.error(
            request,
            f"Only {book.stock} copies available.",
        )

    else:
        cart.add(
            book=book,
            quantity=quantity,
            override_quantity=True,
        )

    return redirect(
        "shop_orders:cart_detail"
    )


@login_required
@require_POST
def cart_remove(request, book_id):
    """Remove a book from the shopping cart."""

    book = get_object_or_404(
        Book,
        id=book_id,
    )

    cart = Cart(request)

    cart.remove(book)

    return redirect(
        "shop_orders:cart_detail"
    )


@login_required
@require_POST
def cart_clear(request):
    """Remove all books from the shopping cart."""

    cart = Cart(request)

    cart.clear()

    return redirect(
        "shop_orders:cart_detail"
    )


def send_order_email(order_id):
    """Send an order confirmation email to the customer."""

    order = Order.objects.get(
        id=order_id,
    )

    if not order.user.email:
        return

    lines = []

    for item in order.items.select_related("book"):
        lines.append(
            (
                f"{item.book.title} "
                f"x {item.quantity} "
                f"= {item.subtotal}"
            )
        )

    items_text = "\n".join(lines)

    message = (
        f"Hello, {order.user.username}!\n\n"
        f"Your order #{order.id} has been created.\n\n"
        f"{items_text}\n\n"
        f"Total: {order.total_amount}\n"
    )

    send_mail(
        subject=f"Order #{order.id} created",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[
            order.user.email,
        ],
        fail_silently=False,
    )


@login_required
@require_POST
def checkout(request):
    """Create an order and Stripe Checkout session from the current cart."""

    cart = Cart(request)

    cart_items = list(cart)

    if not cart_items:
        messages.warning(
            request,
            "Your cart is empty.",
        )

        return redirect(
            "shop_orders:cart_detail"
        )

    with transaction.atomic():

        order = Order.objects.create(
            user=request.user,
        )

        total_amount = Decimal("0.00")

        stripe_items = []

        for cart_item in cart_items:

            book = Book.objects.select_for_update().get(
                id=cart_item["book"].id
            )

            quantity = cart_item["quantity"]

            if book.stock < quantity:
                raise ValueError(
                    (
                        f"Not enough copies of "
                        f"{book.title}. "
                        f"Available: {book.stock}"
                    )
                )

            OrderItem.objects.create(
                order=order,
                book=book,
                price=book.price,
                quantity=quantity,
            )

            item_total = (
                book.price * quantity
            )

            total_amount += item_total

            stripe_items.append(
                {
                    "price_data": {
                        "currency": settings.STRIPE_CURRENCY,
                        "product_data": {
                            "name": book.title,
                        },
                        "unit_amount": int(
                            book.price
                            * Decimal("100")
                        ),
                    },
                    "quantity": quantity,
                }
            )

        order.total_amount = total_amount

        order.save(
            update_fields=[
                "total_amount",
            ]
        )

        transaction.on_commit(
            lambda order_id=order.id:
            send_order_email(order_id)
        )

    client = stripe.StripeClient(
        settings.STRIPE_SECRET_KEY
    )

    try:
        checkout_session = (
            client.v1.checkout.sessions.create(
                params={
                    "mode": "payment",

                    "line_items": stripe_items,

                    "success_url": (
                        request.build_absolute_uri(
                            reverse(
                                "shop_orders:success"
                            )
                        )
                        + "?session_id="
                        + "{CHECKOUT_SESSION_ID}"
                    ),

                    "cancel_url":
                        request.build_absolute_uri(
                            reverse(
                                "shop_orders:cancel"
                            )
                        ),

                    "metadata": {
                        "order_id": str(
                            order.id
                        ),
                    },

                    "customer_email":
                        request.user.email or None,
                }
            )
        )

    except stripe.StripeError as error:

        messages.error(
            request,
            f"Stripe error: {error}",
        )

        return redirect(
            "shop_orders:cart_detail"
        )

    order.stripe_session_id = (
        checkout_session.id
    )

    order.save(
        update_fields=[
            "stripe_session_id",
        ]
    )

    #
    # Stripe Session успешно создана,
    # поэтому очищаем корзину.
    #
    cart.clear()

    return redirect(
        checkout_session.url
    )


@login_required
def checkout_success(request):
    """Display the successful checkout page and related order."""

    session_id = request.GET.get(
        "session_id"
    )

    order = None

    if session_id:
        order = Order.objects.filter(
            stripe_session_id=session_id,
            user=request.user,
        ).first()

    return render(
        request,
        "shop_orders/success.html",
        {
            "order": order,
        },
    )


@login_required
def checkout_cancel(request):
    """Display the checkout cancellation page."""

    return render(
        request,
        "shop_orders/cancel.html",
    )
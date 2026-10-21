from decimal import Decimal

import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .services import send_order_confirmation
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.urls import reverse
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
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
        return HttpResponseBadRequest("Invalid quantity")

    if quantity < 1:
        return HttpResponseBadRequest("Quantity must be at least 1")

    if quantity > book.stock:
        messages.error(
            request,
            f"Only {book.stock} copies available.",
        )

        return redirect("shop_orders:cart_detail")

    cart = Cart(request)

    cart.add(
        book=book,
        quantity=quantity,
    )

    messages.success(
        request,
        f'"{book.title}" added to cart.',
    )

    return redirect("shop_orders:cart_detail")


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
        return HttpResponseBadRequest("Invalid quantity")

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

    return redirect("shop_orders:cart_detail")


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

    return redirect("shop_orders:cart_detail")


@login_required
@require_POST
def cart_clear(request):
    """Remove all books from the shopping cart."""

    cart = Cart(request)

    cart.clear()

    return redirect("shop_orders:cart_detail")


def _release_order_stock(order):
    """
    Return reserved books to stock.

    Call this only while holding a transaction and after confirming
    that the order is still in the created state.
    """
    items = order.items.order_by("book_id")

    for item in items:
        book = Book.objects.select_for_update().get(pk=item.book_id)
        book.stock += item.quantity
        book.save(update_fields=["stock"])


@login_required
@require_POST
@login_required
@require_POST
def checkout(request):
    """Reserve stock, create an order, and start Stripe Checkout."""
    cart = Cart(request)
    cart_items = list(cart)

    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect("shop_orders:cart_detail")

    stripe_items = []
    total_amount = Decimal("0.00")

    try:
        with transaction.atomic():
            order = Order.objects.create(user=request.user)

            # Lock books and reserve stock in one database transaction.
            for cart_item in sorted(
                cart_items,
                key=lambda item: item["book"].id,
            ):
                book = Book.objects.select_for_update().get(pk=cart_item["book"].id)
                quantity = cart_item["quantity"]

                if quantity <= 0 or book.stock < quantity:
                    raise ValueError(f"Not enough copies of {book.title}.")

                book.stock -= quantity
                book.save(update_fields=["stock"])

                OrderItem.objects.create(
                    order=order,
                    book=book,
                    price=book.price,
                    quantity=quantity,
                )

                total_amount += book.price * quantity

                stripe_items.append(
                    {
                        "price_data": {
                            "currency": settings.STRIPE_CURRENCY,
                            "product_data": {
                                "name": book.title,
                            },
                            "unit_amount": int(book.price * Decimal("100")),
                        },
                        "quantity": quantity,
                    }
                )

            order.total_amount = total_amount
            order.save(update_fields=["total_amount"])

    except ValueError as error:
        messages.error(request, str(error))
        return redirect("shop_orders:cart_detail")

    try:
        client = stripe.StripeClient(settings.STRIPE_SECRET_KEY)

        checkout_session = client.v1.checkout.sessions.create(
            params={
                "mode": "payment",
                "line_items": stripe_items,
                "success_url": (
                    request.build_absolute_uri(reverse("shop_orders:success"))
                    + "?session_id={CHECKOUT_SESSION_ID}"
                ),
                "cancel_url": request.build_absolute_uri(reverse("shop_orders:cancel")),
                "metadata": {
                    "order_id": str(order.pk),
                },
                "customer_email": request.user.email or None,
            }
        )

    except stripe.StripeError:
        # Stripe session creation failed: release the reserved stock.
        with transaction.atomic():
            locked_order = Order.objects.select_for_update().get(pk=order.pk)

            if locked_order.status == Order.STATUS_CREATED:
                _release_order_stock(locked_order)
                locked_order.status = Order.STATUS_CANCELLED
                locked_order.save(update_fields=["status"])

        messages.error(
            request,
            "We could not start the payment. Please try again.",
        )
        return redirect("shop_orders:cart_detail")

    # Store the session ID only after Stripe creates the session.
    order.stripe_session_id = checkout_session.id
    order.save(update_fields=["stripe_session_id"])

    cart.clear()
    return redirect(checkout_session.url)


@login_required
def checkout_success(request):
    """Display the successful checkout page and related order."""

    session_id = request.GET.get("session_id")

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


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Process verified Stripe payment and expiration events."""
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    if not webhook_secret:
        return HttpResponse(
            "Stripe webhook is not configured.",
            status=500,
        )

    signature = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(
            request.body,
            signature,
            webhook_secret,
        )
    except (ValueError, stripe.SignatureVerificationError):
        return HttpResponseBadRequest("Invalid Stripe webhook.")

    event_type = event["type"]
    session = event["data"]["object"]

    if event_type not in {
        "checkout.session.completed",
        "checkout.session.expired",
    }:
        return HttpResponse(status=200)

    order_id = session.get("metadata", {}).get("order_id")

    if not order_id:
        return HttpResponse(status=200)

    with transaction.atomic():
        order = Order.objects.select_for_update().filter(pk=order_id).first()

        if order is None:
            return HttpResponse(status=200)

        # Ensure the event belongs to this order's Stripe session.
        if order.stripe_session_id != session.get("id"):
            return HttpResponse(status=200)

        if event_type == "checkout.session.completed":
            # A completed Checkout session is not sufficient by itself.
            if (
                session.get("payment_status") == "paid"
                and order.status == Order.STATUS_CREATED
            ):
                order.status = Order.STATUS_PAID
                order.save(update_fields=["status"])

                # The service queues the email after commit.
                send_order_confirmation(order)

        elif (
            event_type == "checkout.session.expired"
            and order.status == Order.STATUS_CREATED
        ):
            _release_order_stock(order)
            order.status = Order.STATUS_CANCELLED
            order.save(update_fields=["status"])

    return HttpResponse(status=200)

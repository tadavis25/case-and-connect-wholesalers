from decimal import Decimal
import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from products.models import Product
from .forms import OrderForm
from .models import Order, OrderLineItem


def checkout(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        form = OrderForm(request.POST)

    else:
        form = OrderForm()

    bag = request.session.get('bag', {})
    bag_items = []
    total = Decimal('0.00')

    for product_id, quantity in bag.items():
        product = get_object_or_404(Product, pk=product_id)
        subtotal = product.price * quantity
        total += subtotal

        bag_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    amount = int(total * 100)
    if request.method == 'POST' and form.is_valid() and total > 0:
        existing_order_id = request.session.get('pending_order_id')
        if existing_order_id:
            order = Order.objects.filter(
                id=existing_order_id,
                payment_status=False
            ).first()
        else:
            order = None

        if order is None:
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.order_total = total
            order.save()
            request.session['pending_order_id'] = order.id
    else:
        order = None

    intent = None

    if amount > 0 and request.method == 'POST' and form.is_valid():
        intent = stripe.PaymentIntent.create(
            idempotency_key=f"checkout-order-{order.id}",
            amount=amount,
            currency='gbp',
            automatic_payment_methods={'enabled': True},
        )

        if order is not None and intent is not None:
            order.stripe_payment_intent_id = intent.id
            order.save()

    context = {
            'form': form,
            'bag_items': bag_items,
            'total': total,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'client_secret': intent.client_secret if intent else None,
        }

    return render(request, 'checkout/checkout.html', context)


def checkout_success(request):
    payment_intent_id = request.GET.get('payment_intent')
    payment_confirmed = False

    if payment_intent_id:
        order = Order.objects.filter(
            stripe_payment_intent_id=payment_intent_id,
            payment_status=True
        ).first()

        if order:
            payment_confirmed = True
            request.session.pop('bag', None)
            request.session.pop('pending_order_id', None)

    context = {
        'payment_confirmed': payment_confirmed,
    }

    return render(
        request,
        'checkout/checkout_success.html',
        context
    )

from decimal import Decimal
import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from products.models import Product
from .forms import OrderForm
from .models import Order, OrderLineItem
from home.models import CustomerProfile


def checkout(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        form = OrderForm(request.POST)

    else:
        initial_data = {}

        if request.user.is_authenticated:
            profile = CustomerProfile.objects.filter(
                user=request.user
            ).first()

            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }

            if profile:
                initial_data.update({
                    'phone_number': profile.phone_number,
                    'address_line_1': profile.address_line_1,
                    'address_line_2': profile.address_line_2,
                    'town_or_city': profile.town_or_city,
                    'postcode': profile.postcode,
                    'country': profile.country,
                })

        form = OrderForm(initial=initial_data)

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
    print("Checkout total:", total)
    if request.method == 'POST':
        print("Form errors:", form.errors)
        print("Form is valid:", form.is_valid())
        print("Non-field errors:", form.non_field_errors())
        print("Form data:", list(form.data.keys()))
    if request.method == 'POST' and form.is_valid() and total > 0:
        print("Checkout validation passed.")
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

            for product_id, quantity in bag.items():
                product = get_object_or_404(Product, pk=product_id)
                OrderLineItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity
                )
        else:
            order.order_total = total
            order.save()
            order.lineitems.all().delete()
            for product_id, quantity in bag.items():
                product = get_object_or_404(Product, pk=product_id)
                OrderLineItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity
                )

    else:
        order = None

    intent = None

    if amount > 0 and request.method == 'POST' and form.is_valid():
        if order and order.stripe_payment_intent_id:
            intent = stripe.PaymentIntent.retrieve(
                order.stripe_payment_intent_id
            )
            if (
                intent.status == 'requires_payment_method'
                and intent.amount != amount
            ):
                intent = stripe.PaymentIntent.modify(
                    intent.id,
                    amount=amount,
                )
        else:
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
    stripe.api_key = settings.STRIPE_SECRET_KEY
    payment_intent_id = request.GET.get('payment_intent')
    payment_confirmed = False
    order = None

    if payment_intent_id:
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        except stripe.error.StripeError:
            intent = None
        order = Order.objects.filter(
            stripe_payment_intent_id=payment_intent_id,
        ).first()      
        if order and intent and intent.status == 'succeeded':
            if intent.currency == 'gbp' and intent.amount == int(order.order_total * 100):
                order.payment_status = True
                order.save(update_fields=['payment_status'])

        if order and order.payment_status:
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

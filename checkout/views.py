from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from products.models import Product
from .forms import OrderForm


def checkout(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            print("Checkout form is valid")
        else:
            print(form.errors)
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

    context = {
            'form': form,
            'bag_items': bag_items,
            'total': total,
        }

    return render(request, 'checkout/checkout.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product


def view_bag(request):
    bag = request.session.get('bag', {})
    bag_items = []
    total = 0

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
        'bag_items': bag_items,
        'total': total,
    }

    return render(request, 'bag/bag.html', context)


def add_to_bag(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)

        bag = request.session.get('bag', {})
        product_id = str(product.id)

        bag[product_id] = bag.get(product_id, 0) + 1

        request.session['bag'] = bag

    return redirect('view_bag')


def remove_from_bag(request, product_id):
    if request.method == 'POST':
        bag = request.session.get('bag', {})
        product_id = str(product_id)

        if product_id in bag:
            del bag[product_id]
            request.session['bag'] = bag

    return redirect('view_bag')

from django.shortcuts import render
from products.models import Product
from django.contrib.auth.decorators import login_required
from checkout.models import Order

def home(request):
    products = Product.objects.all()[:4]

    context = {
        'products': products,
    }

    return render(request, 'home/index.html', context)


def why_us(request):
    return render(request, 'home/why_us.html')


@login_required
def my_account(request):
    orders = Order.objects.filter(
        user=request.user,
        payment_status=True
    ).order_by('-date')

    context = {
        'orders': orders,
    }

    return render(request, 'home/my_account.html', context)

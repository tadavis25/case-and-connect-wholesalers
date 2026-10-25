from django.shortcuts import render
from products.models import Product


def home(request):
    products = Product.objects.all()[:4]

    context = {
        'products': products,
    }

    return render(request, 'home/index.html', context)

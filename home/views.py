from django.shortcuts import render, redirect
from products.models import Product
from django.contrib.auth.decorators import login_required
from checkout.models import Order
from .forms import AccountDetailsForm, CustomerProfileForm
from .models import CustomerProfile


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
    profile, created = CustomerProfile.objects.get_or_create(
     user=request.user
    )
    orders = Order.objects.filter(
        user=request.user,
        payment_status=True
    ).order_by('-date')

    context = {
         'orders': orders,
         'profile': profile,
    }

    return render(request, 'home/my_account.html', context)


@login_required
def edit_details(request):
    profile, created = CustomerProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':
        form = AccountDetailsForm(
            request.POST,
            instance=request.user
        )
        profile_form = CustomerProfileForm(
            request.POST,
            instance=profile
        )

        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
            return redirect('my_account')
    else:
        form = AccountDetailsForm(instance=request.user)
        profile_form = CustomerProfileForm(instance=profile)

    return render(request, 'home/edit_details.html', {
        'form': form,
        'profile_form': profile_form,
    })

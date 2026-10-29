from django.test import TestCase
from django.urls import reverse
from .models import Order, OrderLineItem


class CheckoutTests(TestCase):

    def test_checkout_page_loads(self):
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)

    def test_checkout_form_valid(self):
        from .forms import OrderForm

        form_data = {
            'full_name': 'Test Customer',
            'email': 'test@example.com',
            'phone_number': '07123456789',
            'address_line_1': '10 Test Street',
            'address_line_2': '',
            'town_or_city': 'London',
            'postcode': 'SW1A 1AA',
            'country': 'United Kingdom',
        }

        form = OrderForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)   

    def test_checkout_form_missing_email(self):
        from .forms import OrderForm

        form_data = {
            'full_name': 'Test Customer',
            'email': '',
            'phone_number': '07123456789',
            'address_line_1': '10 Test Street',
            'address_line_2': '',
            'town_or_city': 'London',
            'postcode': 'SW1A 1AA',
            'country': 'United Kingdom',
        }

        form = OrderForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors) 

    def test_order_line_item_total(self):
        from decimal import Decimal
        from products.models import Product


        product = Product.objects.create(
            name='Test Phone Case',
            price=Decimal('5.99'),
            stock=100,
        )

        order = Order.objects.create(
                    full_name='Test Customer',
                    email='test@example.com',
                    phone_number='07123456789',
                    address_line_1='10 Test Street',
                    town_or_city='London',
                    postcode='SW1A 1AA',
                    country='United Kingdom',
        )
                
        line_item = OrderLineItem(
            order=order,
            product=product,
            quantity=3,
        )

        line_item.save()

        self.assertEqual(
            line_item.lineitem_total,
            Decimal('17.97')
        )

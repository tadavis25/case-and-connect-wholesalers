from django.test import TestCase
from django.urls import reverse
from products.models import Product
from decimal import Decimal


class BagTests(TestCase):

    def setUp(self):
        self.product = Product.objects.create(
            name='Test Phone Case',
            description='A phone case for testing',
            price=5.99,
            stock=10
        )

    def test_update_bag_quantity(self):
        session = self.client.session
        session['bag'] = {str(self.product.id): 1}
        session.save()

        response = self.client.post(
            reverse('update_bag', args=[self.product.id]),
            {'quantity': 3}
        )

        self.assertEqual(response.status_code, 302)

        bag = self.client.session['bag']
        self.assertEqual(bag[str(self.product.id)], 3)

    def test_update_bag_rejects_zero(self):
        session = self.client.session
        session['bag'] = {str(self.product.id): 2}
        session.save()

        self.client.post(
            reverse('update_bag', args=[self.product.id]),
            {'quantity': 0}
        )

        bag = self.client.session['bag']
        self.assertEqual(bag[str(self.product.id)], 2)

    def test_update_bag_rejects_overstock(self):
        session = self.client.session
        session['bag'] = {str(self.product.id): 2}
        session.save()

        self.client.post(
            reverse('update_bag', args=[self.product.id]),
            {'quantity': 11}
        )

        bag = self.client.session['bag']
        self.assertEqual(bag[str(self.product.id)], 2)

    def test_add_product_to_bag(self):
        response = self.client.post(
            reverse('add_to_bag', args=[self.product.id])
        )

        self.assertEqual(response.status_code, 302)

        bag = self.client.session['bag']
        self.assertEqual(bag[str(self.product.id)], 1)

    def test_remove_product_from_bag(self):
        session = self.client.session
        session['bag'] = {str(self.product.id): 2}
        session.save()

        response = self.client.post(
            reverse('remove_from_bag', args=[self.product.id])
        )

        self.assertEqual(response.status_code, 302)

        bag = self.client.session['bag']
        self.assertNotIn(str(self.product.id), bag)

    def test_shopping_bag_total(self):
        session = self.client.session
        session['bag'] = {str(self.product.id): 3}
        session.save()

        response = self.client.get(reverse('view_bag'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total'], Decimal('17.97'))

        bag_items = response.context['bag_items']
        self.assertEqual(bag_items[0]['subtotal'], Decimal('17.97'))

        

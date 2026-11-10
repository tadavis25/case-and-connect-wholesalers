import stripe

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order



@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WH_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']

        print('Webhook PaymentIntent ID:', payment_intent['id'])

        order = Order.objects.filter(
         stripe_payment_intent_id=payment_intent['id']
         ).first()

        print('Webhook found order:', order.id if order else None)

        if order and not order.payment_status:
            order.payment_status = True
            order.save(update_fields=['payment_status'])
            print('Order payment confirmed')

    return HttpResponse(status=200)

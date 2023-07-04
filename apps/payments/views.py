# Django Rest Framework
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes
from rest_framework import status

# SimpleJWT
from rest_framework_simplejwt.authentication import JWTAuthentication

# Third-Party
import stripe
from decouple import config

# Django
from django.conf import settings

# Local
from .models import Payments
from abstract.mixins import ResponseMixin


stripe.api_key = 'sk_test_51NKbuNB7dzpJF5FEiqbFWILqExGMMvBsX1bFgYygGe1y2xX3mRNPYCbYx8zII6K5TtUlb7ELFpODSNyZPU8nUsOZ00Mb0PewLH'
endpoint_secret = 'whsec_2e021f8921a307bb7e61be633c7bb75720352443bc43934a61ed95277d7472cf'


@permission_classes([AllowAny])
class ArtMoney(ResponseMixin, APIView):
    """View for get money."""

    authentication_classes = [JWTAuthentication]

    def get(self, request: Request) -> Response:

        redirect_url = config('PAY_LINK')
        return Response(
            status=status.HTTP_302_FOUND, 
            headers={'Location': redirect_url}
        )


@permission_classes([AllowAny])
class StripeWebhook(ResponseMixin, APIView):

    authentication_classes = [JWTAuthentication]

    def post(self, request):
        # user = request.user
        event = None
        payload = request.data
        sig_header = request.headers['STRIPE_SIGNATURE']
    
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            raise e
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            raise e

        # Handle the event
        if event.type == 'checkout.session.completed':
            session = event.data.object
            # Обработайте завершенный платеж, обновите статус в вашей системе, предоставьте подтверждение пользователю и т. д.
            amount: int = session['amount_total'] / 100
            Payments.objects.create(
                amount=amount,
                user=None,
                status=True
            )
        # Верните успешный ответ для подтверждения получения уведомления от Stripe
        return self.get_json_response(
            key_name='message',
            data={'payment': 'success'},
            status=200
        )


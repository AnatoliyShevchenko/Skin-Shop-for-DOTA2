# Django Rest Framework
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

# SimpleJWT
from rest_framework_simplejwt.authentication import JWTAuthentication

# Third-Party
import stripe
from decouple import config

# Local
from .models import Payments
from .serializers import PaymentSerializer
from abstract.mixins import ResponseMixin
from abstract.paginators import AbstractPaginator
from abstract.validators import APIValidator


@permission_classes([IsAuthenticated])
class PaymentsViewSet(ResponseMixin, ViewSet):
    """ViewSet for Payments."""

    queryset = Payments.objects.all()
    paginator_class = AbstractPaginator()
    authentication_classes = [JWTAuthentication]


    def list(self, request: Request) -> Response:
        """GET Method, not implemented in this view."""

        raise APIValidator(
            'метод list не имплементирован',
            'warning',
            '202'
        )


    def create(self, request: Request) -> Response:
        stripe.api_key = config('PRIVATE_KEY')

        serializer = PaymentSerializer(data=request.data)
        amount = serializer.validated_data('amount')

        if not amount:
            return self.get_json_response(
                key_name='error',
                data='amount is required'
            )
        payment = Payments.objects.create(
            amount=amount,
            status=False,
        )
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='rub',
                payment_method_types=['card']
            )
            payment.status = True
            payment.transaction_id = payment_intent.id
            payment.save()
            
            return self.get_json_response(
                key_name='success',
                data='payment accepted!'
            )
        except stripe.error.CardError as e:
            return self.response_with_critical(
                message=e
            )
        
        except Exception as e:
            return self.response_with_exception(
                message=e
            )
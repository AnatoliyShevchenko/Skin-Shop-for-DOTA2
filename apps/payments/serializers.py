# Django Rest Framework
from rest_framework import serializers

# Local
from .models import Payments


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments."""


    class Meta:
        model = Payments
        fields = ('amount',)
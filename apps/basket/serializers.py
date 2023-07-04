# Django Rest Framework
from rest_framework.serializers import ModelSerializer

# Local
from .models import SkinsBasket, BasketItem
from skins.serializers import SkinsSerializer


class BasketItemSerializer(ModelSerializer):
    """Serializer for basket items."""

    skin = SkinsSerializer()

    class Meta:
        model = BasketItem
        fields = (
            'skin',
            'quantity',
            'price',
            'totalPrice'
        )


class BasketSerializer(ModelSerializer):
    """Serializer for user's basket."""

    basket_items = BasketItemSerializer(many=True)

    class Meta:
        model = SkinsBasket
        fields = (
            'basket_items',
            'total_price'
        )

# Django Rest Framework
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

# SimpleJWT
from rest_framework_simplejwt.authentication import JWTAuthentication

# Django
from django.db import transaction

# Local
from .models import (
    SkinsBasket,
    BasketItem,
)
from .serializers import BasketSerializer
from skins.serializers import SkinsSerializer
from skins.models import Skins, UserSkins
from .utils import get_random_indexes
from abstract.mixins import ResponseMixin
from abstract.paginators import AbstractPaginator


@permission_classes([IsAuthenticated])
class SkinsBasketView(ResponseMixin, APIView):
    """ViewSet for toy basket."""

    paginator_class = AbstractPaginator()
    authentication_classes = [JWTAuthentication]

    def get(self, request: Request) -> Response:
        """GET Method for view basket empty or not."""

        user = request.user

        try:
            basket = SkinsBasket.objects.get(user=user)
            serializer = BasketSerializer(basket)
            return self.get_json_response(
                key_name='basket',
                data=serializer.data,
                status='200'
            )

        except SkinsBasket.DoesNotExist:
            skins = get_random_indexes(40)
            serializer = SkinsSerializer(
                skins,
                many=True
            )
            return self.get_json_response(
                key_name='recommended',
                data=serializer.data,
                status='200'
            )

    def post(self, request: Request) -> Response:
        """POST Method for buy."""

        user = request.user
        try:
            basket = SkinsBasket.objects.get(user=user)
            total_price = basket.total_price

            if user.cash < total_price:
                return self.get_json_response(
                    key_name='error',
                    data='you dont have money for this',
                    status='400'
                )

            with transaction.atomic():
                for item in basket.basket_items.all():
                    UserSkins.objects.create(
                        user=user,
                        skin=item.skin,
                        quantity=item.quantity
                    )
                user.cash -= total_price
                user.save(update_fields=['cash'])
                basket.delete()

            return self.get_json_response(
                key_name='success',
                data='Items purchased successfully',
                status='200'
            )

        except SkinsBasket.DoesNotExist:
            return self.response_with_error(
                message='basket not found'
            )

        except Exception as e:
            return self.response_with_critical(
                message=e
            )

    def put(self, request: Request) -> Response:
        """PUT Method for add skin to basket."""

        user = request.user
        skin_id = request.data.get('skin_id')

        try:
            skin = Skins.objects.get(id=skin_id)

            basket, created = SkinsBasket.objects.get_or_create(
                user=user
            )

            basket_item, item_created = \
                BasketItem.objects.get_or_create(
                    basket=basket,
                    skin=skin,
                    price=skin.realPrice
                )

            if not item_created:
                basket_item.quantity += 1
                basket_item.totalPrice = \
                    basket_item.price * basket_item.quantity
                basket_item.save(
                    update_fields=['totalPrice', 'quantity']
                )
            else:
                basket_item.totalPrice = \
                    basket_item.price * basket_item.quantity
                basket_item.save(
                    update_fields=['totalPrice', 'quantity']
                )
            return self.get_json_response(
                key_name='success',
                data={'message': 'Skin added to basket.'},
                status='200'
            )

        except Skins.DoesNotExist as e:
            return self.response_with_error(
                message=e
            )

        except Exception as e:
            return self.response_with_exception(
                message=e
            )

    def patch(self, request: Request) -> Response:
        """PATCH Method for change items 
        count in basket, or remove item."""

        user = request.user
        skin_id = request.data.get('skin_id')
        action = request.data.get('action')

        try:
            basket_item = BasketItem.objects.get(
                skin_id=skin_id,
                basket__user=user
            )
            if action == 'remove':
                basket_item.delete()
                return self.get_json_response(
                    key_name='success',
                    data='item removed from basket',
                    status='200'
                )
            if action == 'decrease':
                if basket_item.quantity > 1:
                    basket_item.quantity -= 1
                    basket_item.totalPrice = \
                        basket_item.price * basket_item.quantity
                    basket_item.save(
                        update_fields=['quantity', 'totalPrice']
                    )
                    return self.get_json_response(
                        key_name='success',
                        data='item quantity decreased',
                        status='200'
                    )
                else:
                    basket_item.delete()
                    return self.get_json_response(
                        key_name='success',
                        data='item removed from basket',
                        status='200'
                    )
            else:
                return self.get_json_response(
                    key_name='error',
                    data='invalid operation',
                    status='400'
                )

        except BasketItem.DoesNotExist as e:
            return self.response_with_error(
                message='item not found'
            )

        except Exception as e:
            return self.response_with_exception(
                message=e
            )

    def delete(self, request: Request) -> Response:
        """DELETE Metho for clean basket."""

        user = request.user
        try:
            userbasket = SkinsBasket.objects.get(user=user)
            userbasket.delete()
            return self.get_json_response(
                key_name='success',
                data='basket removed',
                status='200'
            )

        except SkinsBasket.DoesNotExist as e:
            return self.response_with_error(
                message=e
            )


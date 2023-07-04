# Django Rest Framework
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser

# SimpleJWT
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

# Django
from django.db.models.query import QuerySet
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# Python
import os

# Third-Party
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Local
from .models import Client, Invites
from .tasks import send_password_reset_email
from auths.models import Client
from skins.models import UserSkins
from .serializers import (
    ClientSerializer,
    ChangePasswordSerializer,
    PersonalSerializer,
    FriendsSerializer,
    InvitesSerializer,
    AuthSerializer,
)
from skins.serializers import CollectionSerializer
from abstract.mixins import ResponseMixin
from abstract.validators import APIValidator
from abstract.paginators import AbstractPaginator


channel_layer = get_channel_layer()


@permission_classes([AllowAny])
class ActivateUser(ResponseMixin, APIView):
    """APIView for Activate user's account."""

    def get(self, request, code, *args, **kwargs):
        """Get Method for activate account."""
        custom_user = Client.objects.filter(
            activation_code=code
        )

        if custom_user:
            user = custom_user[0]
            if not user.is_active:
                user.is_active = True
                user.save()
                async_to_sync(channel_layer.group_send)(
                    'account_activation',
                    {'type': 'send_message'}
                )
                return Response(
                    data={'message': 'Activation success!!!'},
                    status='200'
                )

            return self.response_with_error(
                message='Something went wrong, \
                    please contact us for help.'
            )

        return self.response_with_error(
            message='User cannot be activated, it is not found.'
        )


@permission_classes([AllowAny])
class CustomAuth(TokenObtainPairView):
    """Custom authorization with validation fields."""

    def post(self, request: Request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')

        try:
            user = Client.objects.get(username=username)
            if user.is_active:

                if not user.check_password(password):
                    return Response(
                        data={'Invalid password': 'True'},
                        status='400'
                    )

                try:
                    refresh_token = RefreshToken.for_user(user)
                    access_token = AccessToken.for_user(user)

                except TokenError as e:
                    return Response(
                        data={'error': 'Token generation failed'},
                        status='400'
                    )

                return Response(
                    data={
                        'refresh': str(refresh_token),
                        'access': str(access_token),
                    },
                    status='200'
                )
            return Response(
                data={'error': 'active user not found'},
                status='400'
            )
        except Client.DoesNotExist:
            return Response(
                data={'Invalid username': 'True'},
                status='400'
            )


@permission_classes([AllowAny])
class RegistrationViewset(ResponseMixin, ViewSet):
    """CustomView for registration."""

    queryset: QuerySet = Client.objects.all()

    def list(self, request: Request) -> Response:
        """GET Method, not implemented in this view."""

        raise APIValidator(
            'метод list не имплементирован',
            'warning',
            '202'
        )

    def create(
        self,
        request: Request,
    ) -> Response:
        """POST Method, for registration user."""

        serializer = ClientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            email = serializer.validated_data.get('email')
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            if username == password:
                return self.response_with_error(
                    message='password must be different from username'
                )
            else:
                Client.objects.create_user(
                    email=email,
                    username=username,
                    password=password,
                    cash=1000
                )
                return self.get_json_response(
                    key_name='message',
                    data={
                        'success': 'registration success'
                    },
                    status='200'
                )
        except Exception as e:
            return self.response_with_error(
                message=str(e)
            )


@permission_classes([IsAuthenticated])
class ChangePasswordView(ResponseMixin, APIView):
    """Viewset for changing password."""

    authentication_classes = [JWTAuthentication]

    def patch(self, request: Request):
        """PATCH Method for change password."""

        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.get_json_response(
            key_name='message',
            data={
                'message': 'Password changing success.'
            },
            status='200'
        )


@permission_classes([AllowAny])
class ResetPassword(ResponseMixin, APIView):
    """View for reset password if you forgot it."""

    def post(self, request: Request):
        """POST Method for reset password, 
        it will send mail with new password to email."""

        email = request.data.get('email')
        username = request.data.get('username')
        password = os.urandom(256).hex()[:20]
        users = Client.objects.filter(email=email)
        if not users.exists():
            return self.get_json_response(
                key_name='error',
                data={'email': 'user not found'},
                status='400'
            )
        try:
            user = users.get(username=username)
            user.set_password(password)
            user.save()
            send_password_reset_email.apply_async(
                args=[email, password]
            )
            return self.get_json_response(
                key_name='success',
                data={
                    'message': 'letter was sended to your email'
                },
                status='200'
            )
        except Client.DoesNotExist:
            return self.response_with_error(
                message='username not match with your profile'
            )


@permission_classes([IsAuthenticated])
class PersonalCabView(ResponseMixin, APIView):
    """View for Personal Cabinet."""

    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, JSONParser]

    def get(self, request: Request) -> Response:
        """GET Method for view personal info."""

        user = request.user
        serializer = PersonalSerializer(user)
        return self.get_json_response(
            key_name='user',
            data=serializer.data,
            status='200'
        )

    def patch(self, request: Request) -> Response:
        """Partial update personal info."""

        user = request.user
        serializer = PersonalSerializer(
            instance=user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.get_json_response(
            key_name='success',
            data={'updated': 'info has updated'},
            status='200'
        )

    def delete(self, request: Request) -> Response:
        """Delete account."""

        user = request.user
        user.delete()
        return self.get_json_response(
            key_name='success',
            data={'deleted': 'account removed'},
            status='200'
        )


@permission_classes([IsAuthenticated])
class FriendsView(ResponseMixin, APIView):
    """View for invite and view friends."""

    authentication_classes = [JWTAuthentication]
    pagination_class = AbstractPaginator()

    def get(self, request: Request) -> Response:
        """GET Method for view friends list."""

        user = request.user
        friends = user.friends
        paginator = self.pagination_class
        objects = paginator.paginate_queryset(
            friends,
            request
        )
        serializer = FriendsSerializer(objects)
        return self.get_json_response(
            key_name='friends',
            data=serializer.data,
            paginator=paginator,
            status='200'
        )

    def delete(self, request: Request) -> Response:
        """DELETE Method for kick user of friends list."""

        user = request.user
        friend_id = request.data.get('friend_id')
        if friend_id in user.friends:
            friend = Client.objects.get(id=friend_id)
            user.friends.remove(friend_id)
            user.save(update_fields=['friends'])
            friend.friends.remove(user.id)
            friend.save(update_fields=['friends'])

            return self.get_json_response(
                key_name='success',
                data='friend deleted',
                status='200'
            )

        return self.get_json_response(
            key_name='error',
            data=f'friend with {friend_id} not found.',
            status='404'
        )


@permission_classes([IsAuthenticated])
class InvitesView(ResponseMixin, APIView):
    """View for invite or other functions with invites."""

    authentication_classes = [JWTAuthentication]
    paginator_class = AbstractPaginator()

    def get(self, request: Request) -> Response:
        """GET Method for view invites."""

        user = request.user
        invites = Invites.objects.filter(to_user=user, status=None)
        if invites.exists():
            paginator = self.paginator_class
            objects = paginator.paginate_queryset(
                invites,
                request
            )
            serializer: InvitesSerializer = \
                InvitesSerializer(
                    objects,
                    many=True
                )

            return self.get_json_response(
                key_name='invites',
                data=serializer.data,
                paginator=paginator,
                status='200'
            )
        else:
            return self.get_json_response(
                key_name='invites',
                data='you have no invites for now',
                status='200'
            )

    def post(self, request: Request) -> Response:
        """Create Invite."""

        user = request.user
        username = request.data.get('username')
        friend: QuerySet = Client.objects.filter(
            username=username
        ).first()

        if not friend:
            return self.response_with_error(
                message='user does not exist'
            )

        try:
            Invites.objects.create(
                from_user=user,
                to_user=friend
            )
            return self.get_json_response(
                key_name='success',
                data={'message': 'User has been invited'},
                status='200'
            )
        except Exception as e:
            return self.response_with_error(
                message=str(e)
            )


    def patch(self, request: Request) -> Response:
        """Accept or Reject invite."""

        user = request.user
        username = request.data.get('username')
        action = request.data.get('action')
        friend: QuerySet = Client.objects.filter(
            username=username
        ).first()

        try:
            invite = Invites.objects.get(
                from_user=friend,
                to_user=user
            )
            if action == 'accept':
                Invites.objects.accept_invite(invite)

                return self.get_json_response(
                    key_name='success',
                    data={'message': 'Invite accepted'},
                    status='200'
                )

            elif action == 'reject':
                Invites.objects.reject_invite(invite)
                return self.get_json_response(
                    key_name='success',
                    data={'message': 'Invite rejected'},
                    status='200'
                )
            else:
                return self.response_with_error(
                    message='Invalid action provided'
                )

        except Invites.DoesNotExist:
            return self.response_with_error(
                message='Invite does not exist'
            )


@permission_classes([IsAuthenticated])
class CollectionView(ResponseMixin, APIView):
    """View for skins collection."""

    authentication_classes = [JWTAuthentication]
    pagination_class = AbstractPaginator()

    def get(self, request: Request) -> Response:
        """GET Method for view user's items."""

        user = request.user
        skins: QuerySet = UserSkins.objects.filter(user=user)

        if skins.exists():
            paginator = self.pagination_class
            objects = paginator.paginate_queryset(
                skins,
                request
            )
            serializer: CollectionSerializer = \
                CollectionSerializer(
                    objects,
                    many=True
                )
            return self.get_json_response(
                key_name='my_items',
                data=serializer.data,
                paginator=paginator,
                status='200'
            )

        return self.get_json_response(
            key_name='error',
            data={'message' : 'you have no items'},
            status='200'
        )

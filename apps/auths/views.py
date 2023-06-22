# Django Rest Framework
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

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
                return Response(
                    {'message': 'Activation success!!!'}
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
                    return Response({'Invalid password': 'True'})


                try:
                    refresh_token = RefreshToken.for_user(user)
                    access_token = AccessToken.for_user(user)

                except TokenError as e:
                    return Response({'error': 'Token generation failed'})

                return Response({
                    'refresh': str(refresh_token),
                    'access': str(access_token),
                })
            return Response({'error' : 'active user not found'})
        except Client.DoesNotExist:
            return Response({'Invalid username': 'True'})


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
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return self.get_json_response(
                key_name='message',
                data={
                    'success' : 'registration success'
                }
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
                'message' : 'Password changing success.'
            }
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
                data={'message' : 'user not found'}
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
                    'message' : 'letter was sended to your email'
                }
            )
        except Client.DoesNotExist:
            return self.response_with_error(
                message='username not match with your profile'
            )


@permission_classes([IsAuthenticated])
class PersonalCabView(ResponseMixin, APIView):
    """View for Personal Cabinet."""

    authentication_classes = [JWTAuthentication]

    # @method_decorator(cache_page(600))
    def get(self, request: Request):
        """GET Method for view personal info."""

        user = request.user
        serializer = PersonalSerializer(user)
        return self.get_json_response(
            key_name='user',
            data=serializer.data
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
            paginator=paginator
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
                data='friend deleted'
            )
        
        return self.get_json_response(
            key_name='error',
            data=f'friend with {friend_id} not found.'
        )


@permission_classes([IsAuthenticated])
class InvitesView(ResponseMixin, APIView):
    """View for invite or other functions with invites."""

    paginator_class = AbstractPaginator()

    def get(self, request: Request) -> Response:
        """GET Method for view invites."""

        user = request.user
        invites = Invites.objects.filter(to_user=user)
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
                paginator=paginator
            )
        else:
            return self.get_json_response(
                key_name='invites',
                data='you have no invites for now'
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

        created = Invites.objects.get_or_create(
            from_user=user,
            to_user=friend
        )
        if not created:
            return self.get_json_response(
                key_name='error',
                data={'message': 'Invite already exists'}
            )

        return self.get_json_response(
            key_name='success',
            data={'message': 'User has been invited'}
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
                    data={'message': 'Invite accepted'}
                )

            elif action == 'reject':
                Invites.objects.reject_invite(invite)
                return self.get_json_response(
                    key_name='success',
                    data={'message': 'Invite rejected'}
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
                paginator=paginator
            )
        
        return self.response_with_error(
            message='you have no items'
        )
        
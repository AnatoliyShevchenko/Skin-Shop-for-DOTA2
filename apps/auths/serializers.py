# Django Rest Framework
from rest_framework import serializers

# Django
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

# Python
import logging

# Local
from .models import Client, Invites
from settings.config.config import VALIDATE_PATTERN


User = get_user_model()
logger = logging.getLogger(__name__)



class AuthSerializer(serializers.Serializer):
    """Serializer for custom auth view."""

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        return super().validate(attrs)


class ClientSerializer(serializers.Serializer):
    """Serializer for Client."""
    

    username = serializers.CharField(
        required=True, 
        validators=[RegexValidator(VALIDATE_PATTERN)]
    )
    email = serializers.EmailField(
        required=True, 
        max_length=50
    )
    password = serializers.CharField(
        required=True,
        max_length=32,
        min_length=10,
        validators=[RegexValidator(VALIDATE_PATTERN)]
    )

    def create(self, validated_data):
        user = Client.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            cash=1000
        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""

    old_password = serializers.CharField(
        required=True,
        max_length=32,
        min_length=10,
        validators=[RegexValidator(VALIDATE_PATTERN)]
    )
    new_password = serializers.CharField(
        required=True,
        max_length=32,
        min_length=10,
        validators=[RegexValidator(VALIDATE_PATTERN)]    
    )

    def save(self, **kwargs):
        """Method for change password."""
        try:
            user = self.context['request'].user
            old_password = self.validated_data['old_password']
            new_password = self.validated_data['new_password']
            logger.info(f'User {user.username} \
                is attempting to change password.')
            
            if old_password == new_password:
                raise serializers.ValidationError(
                    'Новый пароль должен отличаться от старого.'
                )
            if not user.check_password(old_password):
                raise serializers.ValidationError(
                    'Неверный текущий пароль.'
                )

            user.set_password(self.validated_data['new_password'])
            user.save()

            logger.info(f'User {user.username} \
                has successfully changed password.')
            return user
        
        except serializers.ValidationError as e:
            logger.error(e)
            raise
        except Exception as e:
            logger.exception(e)
            raise


class OneFriendSerializer(serializers.ModelSerializer):
    """Serializer for a single friend."""

    class Meta:
        model = Client
        fields = (
            'email',
            'first_name',
            'last_name',
            'username',
            'photo',
            'last_login',
        )


class FriendsSerializer(serializers.Serializer):
    """Serializer for viewing friends."""

    friends = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ('friends',)

    def get_friends(self, obj):
        """Method for get user friends."""
        
        friend_ids = obj
        friends = Client.objects.filter(id__in=friend_ids)
        serializer = OneFriendSerializer(friends, many=True)
        return serializer.data
    

class PersonalSerializer(serializers.ModelSerializer):
    """Serializer for Personal Cabinet."""
    
    class Meta:
        model = Client
        fields = (
            'email',
            'first_name',
            'last_name',
            'username',
            'photo',
            'cash',
        )


class UserSerializerForReviews(serializers.ModelSerializer):
    """Serializer for view username on reviews."""

    class Meta:
        model = Client
        fields = (
            'username',
        )


class InvitesSerializer(serializers.ModelSerializer):
    """Serializer for invites."""

    class Meta:
        model = Invites
        fields = ('from_user',)
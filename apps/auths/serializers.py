# Django Rest Framework
from rest_framework import serializers

# Django
from django.core.validators import (
    RegexValidator,
    MinLengthValidator,
    MaxLengthValidator,
)

# Python
import logging

# Local
from .models import Client, Invites
from settings.config.config import VALIDATE_PATTERN


logger = logging.getLogger(__name__)


class AuthSerializer(serializers.Serializer):
    """Serializer for custom auth view."""

    username = serializers.CharField(
        required=True,
        validators=[
            RegexValidator(
                VALIDATE_PATTERN,
                message="username must contain only latin "
                "character(upper and lower register), "
                "symbols and numbers"
            )
        ]
    )
    password = serializers.CharField(
        required=True,
        validators=[
            RegexValidator(
                VALIDATE_PATTERN,
                message="password must contain only latin "
                "character(upper and lower register), "
                "symbols and numbers"
            ),
            MinLengthValidator(
                limit_value=10,
                message="length password must be 10-32 symbols"
            ),
            MaxLengthValidator(
                limit_value=32,
                message="length password must be 10-32 symbols"
            )
        ]
    )

    def validate(self, attrs):
        return super().validate(attrs)


class ClientSerializer(serializers.Serializer):
    """Serializer for Client."""

    username = serializers.CharField(
        required=True,
        validators=[
            RegexValidator(
                VALIDATE_PATTERN,
                message="username must contain only latin "
                "character(upper and lower register), "
                "symbols and numbers"
            )
        ]
    )
    email = serializers.EmailField(
        required=True,
        max_length=100
    )
    password = serializers.CharField(
        required=True,
        validators=[
            RegexValidator(
                VALIDATE_PATTERN,
                message="password must contain only latin "
                "character(upper and lower register), "
                "symbols and numbers"
            ),
            MinLengthValidator(
                limit_value=10,
                message="length password must be 10-32 symbols"
            ),
            MaxLengthValidator(
                limit_value=32,
                message="length password must be 10-32 symbols"
            )
        ]
    )


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""

    old_password = serializers.CharField(
        required=True,
        validators=[
            RegexValidator(
                VALIDATE_PATTERN,
                message="password must contain only latin "
                "character(upper and lower register), "
                "symbols and numbers"
            ),
            MinLengthValidator(
                limit_value=10,
                message="length password must be 10-32 symbols"
            ),
            MaxLengthValidator(
                limit_value=32,
                message="length password must be 10-32 symbols"
            )
        ]
    )
    new_password = serializers.CharField(
        required=True,
        validators=[
            RegexValidator(
                VALIDATE_PATTERN,
                message="password must contain only latin "
                "character(upper and lower register), "
                "symbols and numbers"
            ),
            MinLengthValidator(
                limit_value=10,
                message="length password must be 10-32 symbols"
            ),
            MaxLengthValidator(
                limit_value=32,
                message="length password must be 10-32 symbols"
            )
        ]
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
            if new_password == user.username:
                raise serializers.ValidationError(
                    'Пароль должен отличаться от username.'
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
            'id',
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
            'first_name',
            'last_name',
            'photo',
            'email',
            'username',
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

    from_user = UserSerializerForReviews()

    class Meta:
        model = Invites
        fields = ('from_user',)


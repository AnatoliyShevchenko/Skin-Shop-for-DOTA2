# Django
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin
)
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# Python
from typing import Any
import os


class ClientManager(BaseUserManager):
    """Manager for Clients."""


    def create_user(
        self,
        email: str,
        username: str,
        password: str,
        cash: int
    ) -> 'Client':
        """Registration user."""

        if not email:
            raise ValidationError('Email required')

        user: 'Client' = self.model(
            email=self.normalize_email(email),
        )
        user.username = username
        user.cash = cash
        user.activation_code = os.urandom(20).hex()[:40]
        user.is_active = False
        user.is_staff = False
        user.is_superuser = False
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    
    def create_superuser(
        self,
        email: str,
        username: str,
        password: str
    ) -> 'Client':
        """Create admin."""

        user: 'Client' = self.model(
            email=self.normalize_email(email),
        )
        user.username = username
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save(using=self._db)
        return user


class Client(AbstractBaseUser, PermissionsMixin):
    """Model for Clients."""

    email = models.EmailField(
        max_length=100,
        unique=True,
        verbose_name='почта'
    )
    first_name = models.CharField(
        max_length=20,
        verbose_name='имя',
        null=True,
        blank=True
    )
    last_name = models.CharField(
        max_length=20,
        verbose_name='фамилия',
        null=True,
        blank=True
    )
    username = models.CharField(
        max_length=20,
        verbose_name='имя пользователя',
        unique=True
    )
    photo = models.ImageField(
        upload_to='profiles/photo',
        verbose_name='аватарка',
        null=True,
        blank=True,
    )
    cash = models.PositiveIntegerField(
        verbose_name='кошелёк',
        blank=True,
        null=True,
        default=0
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name='активность'
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name='администратор'
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name='менеджер'
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name='дата регистрации'
    )
    activation_code = models.CharField(
        verbose_name='code',
        max_length=40,
        null=True,
        blank=True
    )
    friends = ArrayField(
        models.IntegerField(),
        blank=True,
        default=list
    )
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = ClientManager()

    class Meta:
        ordering = (
            '-date_joined',
        )
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def save(
        self,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """Custom method for generate activation code."""

        self.full_clean()
        code = os.urandom(20).hex()[:40]
        self.activation_code = code
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.username} {self.email}'
    

class InviteManager(models.Manager):
    """Manager for Invites."""


    def accept_invite(self, invite):
        """Method for accept invite to friends list."""

        from_user = invite.from_user
        to_user = invite.to_user
        invite.status = True

        from_user.friends.append(to_user.id)
        to_user.friends.append(from_user.id)

        from_user.save(update_fields=['friends'])
        to_user.save(update_fields=['friends'])
        invite.save(update_fields=['status'])


    def reject_invite(self, invite):
        """Method for reject invite to friends list."""
        
        invite.status = False
        invite.save(update_fields=['status'])

    
class Invites(models.Model):
    """Model for added friends."""

    from_user = models.ForeignKey(
        to=Client,
        related_name='friend_sent',
        on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        to=Client,
        related_name='friend_received',
        on_delete=models.CASCADE
    )
    date_created = models.DateTimeField(
        auto_now_add=True
    )
    status = models.BooleanField(
        verbose_name='статус приглашения',
        blank=True,
        null=True
    )

    objects = InviteManager()
    
    
    class Meta:
        ordering = ('id',)
        unique_together = ['from_user', 'to_user']
        verbose_name = 'приглашение'
        verbose_name_plural = 'приглашения'


    def __str__(self) -> str:
        return f'{self.from_user} | {self.to_user} | {self.status}'
    

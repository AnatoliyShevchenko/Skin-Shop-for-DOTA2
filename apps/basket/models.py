# Django
from django.db import models
from django.core.validators import (
    MinValueValidator, 
)
from django.utils import timezone

# Local
from skins.models import Skins
from auths.models import Client


class SkinsBasket(models.Model):
    """Model for skins basket."""

    user = models.ForeignKey(
        to=Client,
        on_delete=models.CASCADE,
        verbose_name='пользователь'
    )
    create = models.DateTimeField(
        default=timezone.now,
        verbose_name='дата создания',
    )
    items = models.ManyToManyField(
        to=Skins,
        through='BasketItem',
        verbose_name='скины'
    )
    total_price = models.PositiveIntegerField(
        verbose_name='итоговая цена',
        validators=[MinValueValidator(0)],
        default=0
    )


    class Meta:
        ordering = ('id',)
        verbose_name = 'покупка скинов'
        verbose_name_plural = 'покупка скинов'


    def __str__(self) -> str:
        return f'{self.user.username} | {self.create}'


class BasketItem(models.Model):
    """Intermediate model for items in the basket."""

    basket = models.ForeignKey(
        to=SkinsBasket,
        on_delete=models.CASCADE,
        related_name='basket_items',
        verbose_name='корзина'
    )
    skin = models.ForeignKey(
        to=Skins,
        on_delete=models.PROTECT,
        verbose_name='скин'
    )
    quantity = models.PositiveSmallIntegerField(
        verbose_name='количество',
        default=1,
        validators=[MinValueValidator(1)]
    )
    price = models.PositiveIntegerField(
        verbose_name='цена',
        validators=[MinValueValidator(0)],
        default=0
    )
    totalPrice = models.PositiveIntegerField(
        verbose_name='общая цена',
        validators=[MinValueValidator(0)],
        default=0
    )


    class Meta:
        verbose_name = 'элемент корзины'
        verbose_name_plural = 'элементы корзины'


    def __str__(self) -> str:
        return f'{self.basket} | {self.skin} | {self.quantity}'


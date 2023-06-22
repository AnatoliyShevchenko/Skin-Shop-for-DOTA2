# Django
from django.db import models
from django.core.validators import MinValueValidator


class Payments(models.Model):
    """Model for payments info."""

    amount = models.PositiveIntegerField(
        verbose_name='сумма платежа',
        validators=[MinValueValidator(50)]
    )
    status = models.BooleanField(
        verbose_name='статус платежа',
        blank=True,
        null=True
    )
    transaction_id = models.CharField(
        max_length=100,
        verbose_name='идентификатор транзакции',
        unique=True,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания'
    )

    
    class Meta: 
        ordering = ('id',)
        verbose_name = 'платеж'
        verbose_name_plural = 'платежи'

    
    def __str__(self) -> str:
        return f'{self.transaction_id} | {self.status} \
        | {self.created_at}'
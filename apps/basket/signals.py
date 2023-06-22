# Django
from django.db.models.signals import (
    post_save, 
    post_delete,
)
from django.dispatch import receiver

# Python
import logging

# Local
from .models import BasketItem
from .tasks import update_total_basket_price


logger = logging.getLogger(__name__)


@receiver(
    [post_delete, post_save], 
    sender=BasketItem
)
def update_basket_total_price(
    sender=BasketItem,
    instance=BasketItem,
    **kwargs
) -> None:
    """Signal for update basket total price."""
    
    update_total_basket_price.apply_async(
        args=(instance.basket.user.id,)
    )
    logger.info(f'Total price in {instance.basket.user} updated')
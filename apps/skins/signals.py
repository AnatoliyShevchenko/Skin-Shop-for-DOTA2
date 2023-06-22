# Django
from django.db.models.signals import post_save
from django.dispatch import receiver

# Local
from .models import Reviews, Skins
from .tasks import (
    update_rating, 
    update_total_price,
)

# Python
from typing import Any
import logging


logger = logging.getLogger(__name__)


@receiver(
    post_save,
    sender=Reviews
)
def change_rating(
    sender: Reviews,
    instance: Reviews,
    **kwargs: Any
) -> None:
    """Change skin rating with new review."""

    update_rating.apply_async(
        args=(instance.skin.id,)
    )
    logger.info(f'Rating on skin {instance.skin} changed successful')
    return 


@receiver(
    post_save, 
    sender=Skins
)
def update_total_price_signal(
    sender: Skins, 
    instance: Skins, 
    **kwargs
):
    """Signal for update skin total price."""
    
    changed_fields: dict = instance.changed_fields()
    print(f'ИЗМЕНЕНЫ ПОЛЯ: {changed_fields}')
    if 'priceWithoutSale' in changed_fields\
        or 'sale' in changed_fields:
        print('ПОШЛА ЖАРА')
        update_total_price(instance.id)
        logger.info('total_price has been updated')


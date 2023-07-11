# Python
from settings.celery import app
from .models import BasketItem, SkinsBasket

# Django
from django.db.models import Sum


@app.task
def update_total_basket_price(user_id):
    """Task for update basket total price."""

    basket = SkinsBasket.objects.get(user_id=user_id)
    total_price = BasketItem.objects.filter(
        basket=basket
    ).aggregate(sum_price=Sum('totalPrice'))
    sum_price = total_price['sum_price'] or 0
        
    basket.total_price = sum_price
    basket.save(update_fields=['total_price'])


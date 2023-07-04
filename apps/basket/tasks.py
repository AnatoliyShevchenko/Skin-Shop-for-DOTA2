# Python
from settings.celery import app
from .models import BasketItem, SkinsBasket


@app.task
def update_total_basket_price(user_id):
    """Task for update basket total price."""

    basket = SkinsBasket.objects.get(user_id=user_id)
    total_price = BasketItem.objects.filter(
        basket=basket
    )
    sum_price = 0
    for price in total_price:
        sum_price += price.totalPrice
        
    basket.total_price = sum_price
    basket.save(update_fields=['total_price'])


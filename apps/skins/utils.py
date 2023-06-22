# Django
from django.db.models import QuerySet


def calculate_total_price(obj: QuerySet):
    """Function for calculate total price 
    with changing price or sale."""
    
    total = 0
    if obj.sale > 0:
        print(f'СКИДКА {obj.sale} БЛЯТЬ!')
        total = obj.priceWithoutSale - (
            (obj.priceWithoutSale * obj.sale) / 100
        )
    if obj.sale == 0:
        print('СКИДКИ НЕТ БЛЯТЬ!')
        total = obj.priceWithoutSale
    return int(total)
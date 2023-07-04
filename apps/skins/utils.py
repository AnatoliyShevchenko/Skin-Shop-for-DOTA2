# Django
from django.db.models import QuerySet


def calculate_total_price(obj: QuerySet):
    """Function for calculate total price 
    with changing price or sale."""
    
    total = 0
    if obj.sale > 0:
        total = obj.priceWithoutSale - (
            (obj.priceWithoutSale * obj.sale) / 100
        )
    if obj.sale == 0:
        total = obj.priceWithoutSale
    return int(total)


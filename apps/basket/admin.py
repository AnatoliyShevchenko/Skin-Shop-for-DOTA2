# Django
from django.contrib import admin

# Python
from basket.models import SkinsBasket, BasketItem


class SkinsBasketAdmin(admin.ModelAdmin):
    """Admin panel for skins basket."""

    model = SkinsBasket
    list_display = (
        'user',
        'create',
        'total_price',
    )
    filter_horizontal = ('items',)


class BasketItemAdmin(admin.ModelAdmin):
    """Admin panel for basket items."""

    model = BasketItem
    list_display = (
        'skin',
        'quantity',
        'price',
        'totalPrice',
    )


admin.site.register(SkinsBasket, SkinsBasketAdmin)
admin.site.register(BasketItem, BasketItemAdmin)


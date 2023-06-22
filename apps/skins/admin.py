# Django
from django.contrib import admin

# Local
from .models import (
    Skins, 
    UserSkins, 
    Reviews, 
    Categories,
)


class SkinsAdmin(admin.ModelAdmin):
    """Admin panel for toys."""

    model = Skins
    list_display = (
        'name',
        'id',
        'icon',
        'grade',
        'rating',
        'category',
        'title',
        'image',
        'priceWithoutSale',
        'video',
        'kind',
        'realPrice'
    )
    search_fields = (
        'name',
        'grade',
        'id',
        'rating',
        'category',
        'title',
    )


class RewiewAdmin(admin.ModelAdmin):
    """Admin panel for Rewiews."""

    model = Reviews
    list_display = (
        'user',
        'skin',
        'review',
        'rating',
    )
    search_fields = (
        'user',
        'rating',
        'skin',
    )


class UserSkinsAdmin(admin.ModelAdmin):
    """Admin panel for user's skins."""

    model = UserSkins
    list_display = (
        'skin',
        'quantity',
        'user'
    )
    search_fields = (
        'user',
        'skin'
    )


admin.site.register(Skins, SkinsAdmin)
admin.site.register(UserSkins, UserSkinsAdmin)
admin.site.register(Reviews, RewiewAdmin)
admin.site.register(Categories)


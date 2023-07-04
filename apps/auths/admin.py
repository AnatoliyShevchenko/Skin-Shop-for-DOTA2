# Django
from django.contrib import admin

# Local
from .models import Client, Invites


class ClientAdmin(admin.ModelAdmin):
    """Admin panel for users."""

    model = Client
    list_display = (
        'username', 
        'first_name', 
        'last_name', 
        'email', 
        'cash',
        'is_active', 
        'is_superuser', 
        'is_staff'
    )
    

class InvitesAdmin(admin.ModelAdmin):
    """Admin panel for invites."""

    model = Invites
    list_display = (
        'from_user',
        'to_user',
        'status',
        'date_created'
    )


admin.site.register(Client, ClientAdmin)
admin.site.register(Invites, InvitesAdmin)


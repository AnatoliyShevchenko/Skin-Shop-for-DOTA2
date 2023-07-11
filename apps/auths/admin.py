# Django
from django.contrib import admin
from django.contrib.auth.hashers import make_password

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

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.password = make_password(
                form.cleaned_data['password']
            )
        super().save_model(request, obj, form, change)
    

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


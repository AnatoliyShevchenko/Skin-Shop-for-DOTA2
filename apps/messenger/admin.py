# Django
from django.contrib import admin

# Local
from .models import Messages, ChatRoom


admin.site.register(Messages)
admin.site.register(ChatRoom)
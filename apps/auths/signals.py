# Django
from django.db.models.signals import post_save
from django.dispatch import receiver

# Local
from auths.models import Client, Invites
from .tasks import (
    sending_activate_link, 
    send_invite_message,
    accept_invite_message,
    reject_invite_message,
)

# Python
from typing import Any


@receiver(
    post_save,
    sender=Client,
)
def post_save_user(
    sender: Client,
    instance: Client,
    created: bool,
    **kwargs: Any
) -> None:
    """Signal for send mail with activation link."""

    if created:
        sending_activate_link.apply_async(
            args=(instance.activation_code, instance.email)
        )
        return
        

@receiver(
    post_save,
    sender=Invites
)
def post_save_invite(
    sender: Invites,
    instance: Invites,
    created: bool,
    **kwargs: Any
) -> None:
    """Signal for send invite to friends list message."""
    
    if created:
        send_invite_message.apply_async(
            args=(instance.id,)
        )
        return
    

@receiver(
    post_save,
    sender=Invites
)
def reject_accept_invite(
    sender: Invites,
    instance: Invites,
    created: bool,
    **kwargs: Any
) -> None:
    """Signal for accept or reject invites."""

    if not created:
        if instance.status == True:
            accept_invite_message.apply_async(
                args=(instance.id,)
            )
            return
        if instance.status == False:
            reject_invite_message.apply_async(
                args=(instance.id,)
            )
            return
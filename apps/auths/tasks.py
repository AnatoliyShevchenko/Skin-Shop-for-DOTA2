# Django
from django.core.mail import send_mail
from django.conf import settings

# Python
import logging

# Third-Party
from decouple import config

# Local
from settings.celery import app
from .models import Invites


logger = logging.getLogger(__name__)
APP_HOST = config('APP_HOST')


@app.task
def sending_activate_link(*args):
    """Task for send activation link."""

    send_mail(
        subject='Activation your account on my_diplom',
        message=f'Follow this link for activate \
            {APP_HOST}activate/{args[0]}/',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[args[1]],
        fail_silently=False
    )
    logger.info('MESSAGE: mail was sent')
    print('MESSAGE: mail was sent')


@app.task
def send_invite_message(invite_id):
    """Task for send invite message."""

    invite = Invites.objects.get(id=invite_id)
    from_user = invite.from_user.username
    to_user = invite.to_user.email
    send_mail(
        subject='Invite to friend list',
        message=f'Hello there. User {from_user} \
            has invited you to friend list, \
            please check your invites in personal cabinet.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[to_user],
        fail_silently=False
    )
    logger.info('MESSAGE: Invite success sended.')
    print('MESSAGE: Invite success sended.')


@app.task
def accept_invite_message(invite_id):
    """Task for send mail about accept invite message."""

    invite = Invites.objects.get(id=invite_id)
    from_user = invite.from_user.email
    to_user = invite.to_user.username
    send_mail(
        subject='Your invite accepted!',
        message=f'Hello there. User {to_user} \
            has accepted your invite!',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[from_user],
        fail_silently=False
    )
    logger.info('MESSAGE: Invite accepted.')
    print('MESSAGE: Invite accepted.')


@app.task
def reject_invite_message(invite_id):
    """Task for send mail about reject invite message."""

    invite = Invites.objects.get(id=invite_id)
    from_user = invite.from_user.email
    to_user = invite.to_user.username
    send_mail(
        subject='Your invite rejected!',
        message=f'Hello there. User {to_user} \
            has rejected your invite!',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[from_user],
        fail_silently=False
    )
    logger.info('MESSAGE: Invite rejected.')
    print('MESSAGE: Invite rejected.')


@app.task(
    name='clean-invites'
)
def clean_invites():
    """Task for clean invites database accepted or rejected.
    It works only on mondays."""

    Invites.objects.filter(status=True).delete()
    Invites.objects.filter(status=False).delete()
    logger.info('Invites has cleaned')
    print('Invites has cleaned')


@app.task(
    name='reset-password'
)
def send_password_reset_email(email, password):
    """Task for send mail with new password,
    for user's request about reset password."""
    
    send_mail(
        subject='Reset Password',
        message=f'Hello there. \
            Your password has been changed for your request. \
            Here is new password: {password}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[f'{email}'],
        fail_silently=False
    )
    print('MESSAGE: Password was changed')

    
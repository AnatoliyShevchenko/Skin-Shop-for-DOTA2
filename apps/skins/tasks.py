# Django
from django.core.mail import send_mail
from django.conf import settings

# Python
from datetime import datetime, timedelta

# Local
from settings.celery import app
from .models import Skins, Reviews
from .utils import calculate_total_price
from auths.models import Client


@app.task
def update_rating(skin_id):
    """Task for update skin rating with every new review."""

    skin = Skins.objects.get(id=skin_id)
    reviews = Reviews.objects.filter(skin=skin)
    rating = 0
    if reviews.exists():
        temp = 0
        for review in reviews:
            temp += review.rating
            rating = temp / len(reviews)
    
    skin.rating = rating
    skin.save(update_fields=['rating'])


@app.task(
    name='send-mail-new-skins'
)
def send_mail_about_new_skins():
    """Task to send mail every user about new skins.
    It works every day if new skins was created in a 24 hours."""

    today = datetime.now().replace(
        hour=0, 
        minute=0, 
        second=0, 
        microsecond=0
    )
    yesterday = today - timedelta(days=1)

    new_skins = Skins.objects.filter(
        created_at__gte=yesterday, created_at__lt=today
    )

    if new_skins.exists():
        emails = Client.objects.values_list('email', flat=True)
        send_mail(
            subject='New Skins',
            message='We have a new skins, come and get it.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=emails,
            fail_silently=False
        )
        print('MESSAGE: mail was sent')
    else:
        print('MESSAGE: No new skins found.')

    
@app.task
def update_total_price(skin_id):
    """Task for update skin total price."""
    
    skin = Skins.objects.get(id=skin_id)
    skin.realPrice = calculate_total_price(skin)
    skin.save(update_fields=['realPrice'])
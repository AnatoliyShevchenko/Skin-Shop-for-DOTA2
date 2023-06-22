# Django
from django.db.models import Count

# Python
import random

# Local
from skins.models import Skins


def get_random_indexes(count):
    """Function for get random skins to empty basket."""
    
    total_skins_count = Skins.objects.aggregate(
        total_count=Count('id')
    )['total_count']

    random_indexes = random.sample(
        range(total_skins_count), 
        count
    )

    random_skins = Skins.objects.filter(
        pk__in=random_indexes
    )

    return random_skins
# Python
import requests
from typing import Any
from datetime import datetime
import os

# Django
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile

# Local
from skins.models import Skins, Categories
from settings.config.holy_shit import items as for_generate
from settings.config.another_shit import categories


class Command(BaseCommand):
    """Class to create data."""

    def fill_skins_table(self):
        """Generate data."""

        Skins.objects.all().delete()

        for item in for_generate:
            skin = Skins(
                title=item['title'],
                name=item['name'],
                rating=0,
                grade=item['grade'],
                category=item['category'],
                content=item['content'],
                version=item['version'],
                history=item['history'],
                kind=item['kind'],
                priceWithoutSale=item['price'],
                sale=item['sale'],
            )
            if item['sale'] > 0:
                skin.realPrice = item['price'] - (
                    (item['price'] * item['sale']) / 100
                )
            if item['sale'] == 0:
                skin.realPrice = item['price']
            icon_url = item['icon']
            if icon_url:
                icon_content = requests.get(
                    icon_url, 
                    stream=True
                ).content
                skin.icon.save(
                    f"{item['name']}.png", 
                    ContentFile(icon_content), 
                    save=True
                )

            img_url = item['image']
            if img_url:
                img_content = requests.get(
                    img_url, 
                    stream=True
                ).content
                skin.image.save(
                    f"{item['name']}.png", 
                    ContentFile(img_content), 
                    save=True
                )

            video_url = item['video']
            if video_url:
                video_name = os.urandom(20).hex()[:10]
                video_content = requests.get(
                    video_url, 
                    stream=True
                ).content
                skin.video.save(
                    f"{video_name}.mp4", 
                    ContentFile(video_content), 
                    save=True
                )

            skin.save()
            print(f"Skin named {item['name']} created!!!")
        

    def fill_categories(self):

        Categories.objects.all().delete()

        for category in categories:
            obj = Categories(
                name=category['name'],
                number=category['number']
            )

            icon_url = category['img']
            if icon_url:
                icon_content = requests.get(
                    icon_url,
                    stream=True
                ).content
                obj.image.save(
                    f'{category["name"]}.png',
                    ContentFile(icon_content),
                    save=True
                )
            obj.save()
            print(f'Category named {category["name"]} created!!!')


    def handle(self, *args: Any, **kwargs: Any) -> None:
        """Handles data filling."""

        start: datetime = datetime.now()
        self.fill_skins_table()
        self.fill_categories()
        print(
            f'Generated in: \
                {(datetime.now()-start).total_seconds()} seconds.'
        )


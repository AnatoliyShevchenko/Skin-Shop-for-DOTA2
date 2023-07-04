# Django
from django.core.validators import (
    MinValueValidator, 
    MaxValueValidator,
)
from django.db import models
from django.utils import timezone

# Third-Party
from dirtyfields import DirtyFieldsMixin

# Local
from auths.models import Client


class Skins(DirtyFieldsMixin, models.Model):
    """Class for Skins."""

    icon = models.ImageField(
        upload_to='skins/icons',
        verbose_name='иконки',
        default=''
    )
    title = models.CharField(
        verbose_name='название',
        max_length=100
    )
    name = models.CharField(
        verbose_name='имя',
        max_length=100
    )
    grade = models.CharField(
        verbose_name='градация',
        max_length=50
    )
    rating = models.PositiveSmallIntegerField(
        verbose_name='оценка',
        null=False,
        validators=[MaxValueValidator(5)]
    )
    category = models.PositiveSmallIntegerField(
        verbose_name='категория',
        null=False
    )
    image = models.ImageField(
        upload_to='skins/images',
        verbose_name='изображение',
        default='',
    )
    video = models.FileField(
        upload_to='skins/videos',
        verbose_name='видео',
        default='',
        null=True,
        blank=True
    )
    content = models.TextField(
        max_length=1000,
        verbose_name='контент',
        null=True,
        blank=True
    )
    version = models.TextField(
        verbose_name='версия',
        max_length=500,
        null=True,
        blank=True
    )
    history = models.TextField(
        verbose_name='история',
        max_length=1000,
        null=True,
        blank=True
    )
    kind = models.CharField(
        verbose_name='что это вообще',
        max_length=200,
        null=True,
        blank=True
    )
    priceWithoutSale = models.PositiveBigIntegerField(
        verbose_name='цена',
        null=False
    )
    sale = models.PositiveSmallIntegerField(
        verbose_name='скидка',
        null=True
    )
    realPrice = models.PositiveBigIntegerField(
        verbose_name='итоговая цена',
        null=True
    )
    created_at = models.DateTimeField(
        verbose_name='дата создания',
        default=timezone.now
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'скин'
        verbose_name_plural = 'скины'

    def changed_fields(self):
        """Method for get changed fields."""

        return self.get_dirty_fields()

    def __str__(self) -> str:
        return self.title
    

class UserSkins(models.Model):
    """Model for user's skins."""

    user = models.ForeignKey(
        to=Client,
        related_name='user',
        verbose_name='пользователь',
        on_delete=models.CASCADE
    )
    skin = models.ForeignKey(
        to=Skins,
        related_name='skins',
        verbose_name='скины',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        verbose_name='количество',
        default=1,
        validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'скин пользователя'
        verbose_name_plural = 'скины пользователя'

    def __str__(self) -> str:
        return self.user.username
    
    
class Reviews(models.Model):
    """Class for user's rewiew."""

    user = models.ForeignKey(
        to=Client,
        related_name='user_review',
        verbose_name='пользователь',
        on_delete=models.CASCADE,
    )
    skin = models.ForeignKey(
        to=Skins,
        on_delete=models.CASCADE,
        related_name='skin_review',
        verbose_name='скин',
    )
    review = models.TextField(
        verbose_name='отзыв',
        max_length=2000,
        blank=True,
        null=True
    )
    rating = models.PositiveSmallIntegerField(
        verbose_name='оценка',
        blank=False,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'
        unique_together = ('user', 'skin')

    def __str__(self) -> str:
        return f"{self.user.username}|{self.rating}" 
    

class Categories(models.Model):
    """Model for categories."""

    name = models.CharField(
        verbose_name='название категории',
        max_length=200
    )
    image = models.ImageField(
        upload_to='media/categories',
        verbose_name='иконка',
        default=''
    )
    number = models.PositiveSmallIntegerField(
        verbose_name='типа идентификатор',
        unique=True
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self) -> str:
        return self.name
    

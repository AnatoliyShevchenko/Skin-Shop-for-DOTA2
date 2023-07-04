# Django Rest Framework
from rest_framework import serializers

# Local
from .models import (
    Skins, 
    Reviews, 
    UserSkins, 
    Categories,
)
from auths.serializers import UserSerializerForReviews


class FiltersSerializer(serializers.Serializer):
    """Serializer for validation filters."""

    category = serializers.CharField(required=False)
    search = serializers.CharField(required=False)
    order = serializers.ChoiceField(
        choices=['asc', 'desc'], 
        required=False
    )
    sortBy = serializers.ChoiceField(
        choices=['realPrice'], 
        required=False
    )

    class Meta:
        fields = (
            'category',
            'search',
            'order',
            'sortBy',
        )


class SkinsSerializer(serializers.ModelSerializer):
    """Serializer for Skins."""

    class Meta:
        model = Skins
        fields = (
            'id',
            'icon',
            'title',
            'name',
            'grade',
            'rating',
            'category',
            'image',
            'priceWithoutSale',
            'sale',
            'realPrice',
        )


class CollectionSerializer(serializers.ModelSerializer):
    """Serializer for my items collection."""

    skin = SkinsSerializer()

    class Meta:
        model = UserSkins
        fields = (
            'skin',
            'quantity',
        )


class SkinForReviewSerializer(serializers.ModelSerializer):
    """Serializer for view skin name in reviews."""

    class Meta:
        model = Skins
        fields = (
            'name',
        )


class ReviewsSerializer(serializers.ModelSerializer):
    """Serializer for all reviews."""

    user = UserSerializerForReviews()
    skin = SkinForReviewSerializer()

    class Meta:
        model = Reviews
        fields = (
            'user',
            'skin',
            'rating',
            'review',    
        )
        read_only_fields = (
            'user',
            'skin',
            'rating',
            'review',    
        )


class CreateReviewSerializer(serializers.ModelSerializer):
    """Serializer for create review."""

    skin_id = serializers.IntegerField()

    class Meta:
        model = Reviews
        fields = (
            'skin_id',
            'rating',
            'review'
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for view reviews in retrieve skins method."""

    user = UserSerializerForReviews()

    class Meta:
        model = Reviews
        fields = (
            'user',
            'rating',
            'review',    
        )


class SkinRetrieveSerial(serializers.ModelSerializer):
    """Serializer for retrieve method."""

    class Meta:
        model = Skins
        fields = (
            'icon',
            'title',
            'name',
            'grade',
            'rating',
            'category',
            'image',
            'video',
            'content',
            'version',
            'history',
            'kind',
            'priceWithoutSale',
            'sale',
            'realPrice',
        )


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for view categories."""

    class Meta:
        model = Categories
        fields = (
            'name',
            'image',
            'number'
        )

        
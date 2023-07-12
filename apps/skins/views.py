# Django Rest Framework
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

# SimpleJWT
from rest_framework_simplejwt.authentication import JWTAuthentication

# Django
from django.db.models.query import QuerySet
from django.core.cache import cache
from django.shortcuts import get_object_or_404

# Local
from .models import (
    Skins,
    Reviews,
    Categories,
)
from .serializers import (
    SkinsSerializer,
    SkinRetrieveSerial,
    ReviewsSerializer,
    FiltersSerializer,
    ReviewSerializer,
    CategorySerializer,
    CreateReviewSerializer,
)
from abstract.mixins import ResponseMixin
from abstract.paginators import AbstractPaginator


@permission_classes([AllowAny])
class SkinsViewSet(ResponseMixin, ViewSet):
    """ViewSet for Skins."""

    queryset: QuerySet = Skins.objects.all()
    paginator_class = AbstractPaginator()
    authentication_classes = [JWTAuthentication]

    def list(self, request: Request, *args, **kwargs) -> Response:
        """GET Method for view skin list."""

        cache_key = 'all_skins'
        try:
            skins = cache.get(key=cache_key)
            if not skins:
                skins = self.queryset.all()
                cache.set(key=cache_key, value=skins, timeout=600)

            serializer = FiltersSerializer(data=request.query_params)
            if serializer.is_valid():
                category = serializer.validated_data.get('category')
                search = serializer.validated_data.get('search')
                order = serializer.validated_data.get('order')
                sortBy = serializer.validated_data.get('sortBy')

                if sortBy == 'realPrice':
                    if order == 'desc':
                        skins = skins.order_by('-realPrice')
                    elif order == 'asc':
                        skins = skins.order_by('realPrice')
                if category:
                    skins = skins.filter(category=category)

                if search:
                    skins = skins.filter(name__icontains=search)

                paginator = self.paginator_class
                objects: list = paginator.paginate_queryset(
                    skins,
                    request
                )
                serializer: SkinsSerializer = \
                    SkinsSerializer(
                        objects,
                        many=True
                    )
                return self.get_json_response(
                    key_name='items',
                    data=serializer.data,
                    paginator=paginator,
                    status='200'
                )

            else:
                errors = serializer.errors
                return self.response_with_error(
                    message=errors
                )

        except Exception as e:
            return self.response_with_exception(
                message=e
            )

    def retrieve(self, request: Request, pk: str) -> Response:
        """GET Method for view one skin."""

        cache_key = f'skin_{pk}_info'
        try:
            skin = cache.get(key=cache_key)
            if not skin:
                skin = self.queryset.get(id=pk)
                cache.set(key=cache_key, value=skin)
            serializer = SkinRetrieveSerial(skin)
            data = serializer.data
            return self.get_json_response(
                key_name='item',
                data=data,
                status='200'
            )

        except Skins.DoesNotExist:
            error_message = f'Skin with id {pk} does not exist.'
            return self.response_with_error(
                message=error_message
            )


@permission_classes([IsAuthenticated])
class ReviewsViewSet(ResponseMixin, ViewSet):
    """Viewset for user's review."""

    queryset = Reviews.objects.all()
    paginator_class = AbstractPaginator()
    authentication_classes = [JWTAuthentication]

    # def list(self, request: Request, *args, **kwargs) -> Response:
    #     """Get method for view reviews list."""

    #     try:
    #         reviews = self.queryset.all()

    #         paginator = self.paginator_class
    #         objects: list = paginator.paginate_queryset(
    #             reviews,
    #             request
    #         )
    #         serializer = ReviewsSerializer(objects, many=True)
    #         return self.get_json_response(
    #             data=serializer.data,
    #             key_name='reviews',
    #             paginator=paginator,
    #             status='200'
    #         )

    #     except Exception as e:
    #         return self.response_with_exception(
    #             message=e
    #         )

    def retrieve(self, request: Request, pk: str) -> Response:
        """View reviews about skin."""

        cache_key = f'skin_{pk}_reviews'
        reviews = cache.get(key=cache_key)
        if not reviews:
            reviews = self.queryset.filter(skin__id=pk)
            cache.set(key=cache_key, value=reviews)
        paginator = self.paginator_class
        objects = paginator.paginate_queryset(
            reviews,
            request
        )
        serializer = ReviewSerializer(
            objects,
            many=True
        )
        return self.get_json_response(
            key_name='reviews',
            data=serializer.data,
            status='200'
        )
        
    def create(self, request: Request) -> Response:
        """Create review to skin."""

        serializer = CreateReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        skin_id = serializer.validated_data.get('skin_id')
        text_review = serializer.validated_data.get('review')
        skin_rating = serializer.validated_data.get('rating')

        skin = get_object_or_404(Skins, id=skin_id)

        new_review, created = Reviews.objects.get_or_create(
            skin=skin,
            user=user,
            defaults={
                'review': text_review,
                'rating': skin_rating
            }
        )

        if not created:
            new_review.review = text_review
            new_review.rating = skin_rating
            new_review.save()
        
        cache.delete_many([
            f'skin_{skin_id}_reviews', 
            f'skin_{skin_id}_info'
        ])
        return self.get_json_response(
            key_name='success',
            data={'message': 'Review has been published.'},
            status='200'
        )


@permission_classes([AllowAny])
class CategoryViewSet(ResponseMixin, ViewSet):
    """ViewSet for view categories."""

    queryset = Categories.objects.all()
    authentication_classes = [JWTAuthentication]

    def list(self, request: Request) -> Response:

        cache_key = 'categories'
        categories = cache.get('categories')
        if not categories:
            categories = self.queryset.all()
            if not categories.exists():
                return self.get_json_response(
                    key_name='error',
                    data={'error': 'Категории не найдены'},
                    status='400'
                )

            cache.set(
                key=cache_key, 
                value=categories, 
                timeout=60*60
            )
            
        serializer = CategorySerializer(
            categories,
            many=True
        )
        return self.get_json_response(
            key_name='categories',
            data=serializer.data,
            status='200'
        )
        

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
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.exceptions import FieldError

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

    @method_decorator(cache_page(600))
    def list(self, request: Request, *args, **kwargs) -> Response:
        """GET Method for view skin list."""

        try:
            skins = self.queryset.all()
            serializer = FiltersSerializer(data=request.query_params)
            if serializer.is_valid():
                category = serializer.validated_data.get('category')
                search = serializer.validated_data.get('search')
                order = serializer.validated_data.get('order')
                sortBy = serializer.validated_data.get('sortBy')

                if sortBy == 'realPrice':
                    if order == 'desc':
                        skins = skins.order_by('-priceWithoutSale')
                    elif order == 'asc':
                        skins = skins.order_by('priceWithoutSale')
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

    # @method_decorator(cache_page(600))
    def retrieve(self, request: Request, pk: str) -> Response:
        """GET Method for view one skin."""

        try:
            skin = self.queryset.get(id=pk)
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

    # @method_decorator(cache_page(600))
    def list(self, request: Request, *args, **kwargs) -> Response:
        """Get method for view reviews list."""

        try:
            reviews = self.queryset.all()

            paginator = self.paginator_class
            objects: list = paginator.paginate_queryset(
                reviews,
                request
            )
            serializer = ReviewsSerializer(objects, many=True)
            return self.get_json_response(
                data=serializer.data,
                key_name='reviews',
                paginator=paginator,
                status='200'
            )

        except Exception as e:
            return self.response_with_exception(
                message=e
            )

    # @method_decorator(cache_page(600))
    def retrieve(self, request: Request, pk: str) -> Response:
        """View reviews about skin."""

        try:
            skin = Skins.objects.get(id=pk)
            reviews = self.queryset.filter(skin=skin)
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
        except Skins.DoesNotExist:
            return self.get_json_response(
                key_name='error',
                data={'message': 'skin does not exist'},
                status='400'
            )

    def create(self, request: Request) -> Response:
        """Create review to skin."""

        serializer = CreateReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        skin_id = serializer.validated_data.get('skin_id')
        text_review = serializer.validated_data.get('review')
        skin_rating = serializer.validated_data.get('rating')
        try:
            skin = Skins.objects.get(id=skin_id)
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

            return self.get_json_response(
                key_name='success',
                data={'message': 'Review has been published.'},
                status='200'
            )
        except Skins.DoesNotExist:
            error_message = \
                f'Skin with id {skin_id} does not exist.'
            return self.response_with_error(
                message=error_message
            )
        except FieldError as e:
            return self.response_with_error(
                message=str(e)
            )
        except Exception as e:
            return self.response_with_exception(
                message=e,
                status='200'
            )


@permission_classes([AllowAny])
class CategoryViewSet(ResponseMixin, ViewSet):
    """ViewSet for view categories."""

    queryset = Categories.objects.all()
    authentication_classes = [JWTAuthentication]

    @method_decorator(cache_page(600))
    def list(self, request: Request) -> Response:
        categories = self.queryset.all()
        if categories:
            serializer = CategorySerializer(
                categories,
                many=True
            )
            return self.get_json_response(
                key_name='categories',
                data=serializer.data,
                status='200'
            )
        return self.get_json_response(
            key_name='error',
            data={'error': 'categories not found'},
            status='400'
        )

# Django
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

# Django Rest Framework
from rest_framework.routers import DefaultRouter

# SimpleJWT
from rest_framework_simplejwt.views import TokenRefreshView

# Local
from auths.views import (
    RegistrationViewset,
    ChangePasswordView,
    PersonalCabView,
    ActivateUser,
    FriendsView,
    InvitesView,
    CollectionView,
    ResetPassword,
    CustomAuth,
)
from basket.views import SkinsBasketView
# from messenger.views import MessagesViewSet
from payments.views import (
    ArtMoney,
    StripeWebhook,
)
from skins.views import (
    SkinsViewSet,
    ReviewsViewSet,
    CategoryViewSet,
)


router: DefaultRouter = DefaultRouter(
    trailing_slash=True
)
router.register('items', SkinsViewSet)
router.register('registration', RegistrationViewset)
router.register('reviews', ReviewsViewSet)
router.register('categories', CategoryViewSet)
# router.register('messages', MessagesViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='main.html')),
    path('api/v1/', include(router.urls)),
    path('api/v1/reset-password/', ResetPassword.as_view()),
    path('api/v1/change-password/', ChangePasswordView.as_view()),
    path('api/v1/per-cab/', PersonalCabView.as_view()),
    path('api/v1/invites/', InvitesView.as_view()),
    path('api/v1/friends/', FriendsView.as_view()),
    path('api/v1/collection/', CollectionView.as_view()),
    path('api/v1/basket/', SkinsBasketView.as_view()),
    path('api/v1/art-money/', ArtMoney.as_view()),
    path('api/v1/webhook/', StripeWebhook.as_view()),
    path('api/token/', CustomAuth.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
    path('activate/<str:code>/', ActivateUser.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]


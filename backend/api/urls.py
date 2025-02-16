from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'auth', views.AuthViewSet, basename='auth')
router.register(r'documents', views.DocumentViewSet, basename='document')
router.register(r'suggestions', views.SuggestionViewSet, basename='suggestion')
router.register(r'profile', views.ProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
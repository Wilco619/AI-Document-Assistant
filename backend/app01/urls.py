from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, AdminUserViewSet, PasswordChangeView, ProcessedDocumentViewSet, UserInfoAPIView, UserLogOutAPIView, UserRegistrationView
from .views import CreateAdminUserView,  LoginView, VerifyOTPView


from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'admins-list', AdminUserViewSet)
router.register(r'processed-documents', ProcessedDocumentViewSet, basename='processed-document')



urlpatterns = [
    path('list/', include(router.urls)),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', UserLogOutAPIView.as_view(), name='logout_user'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),
    path('user/', UserInfoAPIView.as_view(), name='user-info'),
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('create-admin/', CreateAdminUserView.as_view(), name='create-admin-user'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),  # Added endpoint for OTP verification   

  # New URL for the dashboard

]

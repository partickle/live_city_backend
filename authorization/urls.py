from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from authorization.views import (DeleteAccountView, ResetPasswordView, RegisterAPIView, LoginAPIView,
                                 SendVerificationCodeView, VerifyVerificationCodeView, AdminLoginAPIView,
                                 UserListAPIView, UserDeactivateAPIView)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('send-activation/', SendVerificationCodeView.as_view(), name='send-activation-code'),
    path('verify/', VerifyVerificationCodeView.as_view(), name='verify-activation-code'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('admin/login/', AdminLoginAPIView.as_view(), name='admin_login'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('delete/', DeleteAccountView.as_view(), name='delete_account'),

    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('users/<int:user_id>/deactivate/', UserDeactivateAPIView.as_view(), name='user-deactivate'),
]

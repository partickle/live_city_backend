from django.urls import path
from .views import UserPointCreateAPIView, UserPointModerationAPIView, UserPointListAPIView

urlpatterns = [
    path('user-points/create/', UserPointCreateAPIView.as_view(), name='user-point-create'),
    path('user-points/moderate/<int:pk>/', UserPointModerationAPIView.as_view(), name='user-point-moderate'),
    path('user-points/', UserPointListAPIView.as_view(), name='user-point-list'),
]
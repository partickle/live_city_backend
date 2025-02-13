from django.urls import path
from .views import (
    CategoryListAPIView, CategoryDetailAPIView,
    PointListAPIView, PointDetailAPIView,
    UserPointsAPIView
)

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='category_list'),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='category_detail'),

    path('points/', PointListAPIView.as_view(), name='point_list'),
    path('points/<int:pk>/', PointDetailAPIView.as_view(), name='point_detail'),

    path('user/points/', UserPointsAPIView.as_view(), name='user_points'),

]

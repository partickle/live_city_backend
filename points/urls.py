from django.urls import path
from .views import (
    CategoryListAPIView, CategoryDetailAPIView,
    PointListAPIView, PointDetailAPIView,
    CheckInAPIView, UserVisitedPointsAPIView, ArticleDetailAPIView
)

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='category_list'),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='category_detail'),

    path('points/', PointListAPIView.as_view(), name='point_list'),
    path('points/<int:pk>/', PointDetailAPIView.as_view(), name='point_detail'),

    path('check-in/', CheckInAPIView.as_view(), name='check-in'),
    path('visited_points/', UserVisitedPointsAPIView.as_view(), name='visited_points'),

    path('articles/<int:pk>/', ArticleDetailAPIView.as_view(), name='article-detail'),
]

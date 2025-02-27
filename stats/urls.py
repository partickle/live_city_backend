from django.urls import path
from .views import (

    StatisticsAPIView)

urlpatterns = [

    path('stats_admin/', StatisticsAPIView.as_view(), name='stats'),

]

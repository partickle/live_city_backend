from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from django.contrib.auth.models import User
from points.models import VisitedPoint
from .models import Statistics
from .serializers import StatisticsSerializer

User = get_user_model()


class StatisticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        total_users = User.objects.count()
        total_visits = VisitedPoint.objects.count()

        visits_per_point = VisitedPoint.objects.values('point__name').annotate(
            total_visits=Count('id')
        ).order_by('-total_visits')

        top_points = visits_per_point[:5]

        statistics = Statistics.update_statistics(
            total_users=total_users,
            total_visits=total_visits,
            visits_per_point=list(visits_per_point),
            top_points=list(top_points),
        )

        serializer = StatisticsSerializer(statistics)
        return Response(serializer.data, status=status.HTTP_200_OK)

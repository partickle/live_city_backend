from rest_framework import serializers
from .models import Statistics


class StatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistics
        fields = ['total_users', 'total_visits', 'visits_per_point', 'top_points', 'created_at']


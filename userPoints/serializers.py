from rest_framework import serializers
from .models import UserPoint


class UserPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPoint
        fields = ['id', 'user', 'name', 'latitude', 'longitude', 'start_time', 'end_time', 'is_active']
        read_only_fields = ['id', 'user', 'is_active']

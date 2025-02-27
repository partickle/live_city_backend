import logging

from django.db import transaction
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Category, Point, VisitedPoint
from .serializers import CategorySerializer, PointSerializer, VisitedPointSerializer, CheckInSerializer
from drf_yasg.utils import swagger_auto_schema
from geopy.distance import geodesic

logger = logging.getLogger(__name__)

class CategoryListAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            serializer.save()
        else:
            raise PermissionError("You do not have permission to create a category.")


class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super().put(request, *args, **kwargs)
        else:
            return Response({"detail": "You do not have permission to update this category."},
                            status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super().delete(request, *args, **kwargs)
        else:
            return Response({"detail": "You do not have permission to delete this category."},
                            status=status.HTTP_403_FORBIDDEN)


class PointListAPIView(generics.ListCreateAPIView):
    queryset = Point.objects.all()
    serializer_class = PointSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            serializer.save()
        else:
            raise PermissionError("You do not have permission to create a point.")


class PointDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Point.objects.all()
    serializer_class = PointSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super().put(request, *args, **kwargs)
        else:
            return Response({"detail": "You do not have permission to update this point."},
                            status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super().delete(request, *args, **kwargs)
        else:
            return Response({"detail": "You do not have permission to delete this point."},
                            status=status.HTTP_403_FORBIDDEN)


class UserPointsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: PointSerializer(many=True)})
    def get(self, request, *args, **kwargs):
        points = Point.objects.filter(user=request.user)
        serializer = PointSerializer(points, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserVisitedPointsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: VisitedPointSerializer(many=True)})
    def get(self, request, *args, **kwargs):
        visited_points = VisitedPoint.objects.filter(user=request.user)
        serializer = VisitedPointSerializer(visited_points, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CheckInAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=CheckInSerializer,
        responses={200: "Check-in successful", 400: "Error"}
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = CheckInSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        point_id = serializer.validated_data["point_id"]
        latitude = float(serializer.validated_data["latitude"])
        longitude = float(serializer.validated_data["longitude"])

        try:
            point = Point.objects.get(id=point_id)
        except Point.DoesNotExist:
            return Response({"error": "Точка не найдена"}, status=status.HTTP_404_NOT_FOUND)

        user_location = (latitude, longitude)
        point_location = (float(point.latitude), float(point.longitude))
        distance = geodesic(user_location, point_location).meters

        if distance > 100:
            return Response({"error": "Вы слишком далеко от точки"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            visit, created = VisitedPoint.objects.get_or_create(user=user, point=point)
            if not created:
                return Response({"message": "Вы уже отмечались в этой точке"}, status=status.HTTP_400_BAD_REQUEST)

            user.level += point.exp // 100
            user.save()

        return Response({"message": "Вы успешно отметились!", "new_level": user.level}, status=status.HTTP_200_OK)

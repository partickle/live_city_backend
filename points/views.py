from django.db import transaction
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Category, Point, VisitedPoint, Article
from .serializers import CategorySerializer, PointSerializer, VisitedPointSerializer, CheckInSerializer, \
    ArticleSerializer
from drf_yasg.utils import swagger_auto_schema
from geopy.distance import geodesic
from rest_framework.parsers import MultiPartParser, FormParser


class CategoryListAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            serializer.save()
        else:
            return Response({"detail": "У вас нет прав на создание категории."},
                            status=status.HTTP_403_FORBIDDEN)


class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super().put(request, *args, **kwargs)
        else:
            return Response({"detail": "У вас нет прав на обновление этой категории."},
                            status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super().delete(request, *args, **kwargs)
        else:
            return Response({"detail": "У вас нет прав на удаление этой категории."},
                            status=status.HTTP_403_FORBIDDEN)


class PointListAPIView(generics.ListCreateAPIView):
    queryset = Point.objects.all()
    serializer_class = PointSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            serializer.save()
        else:
            return Response({"detail": "У вас нет прав на создание точки."},
                            status=status.HTTP_403_FORBIDDEN)


class PointDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Point.objects.all()
    serializer_class = PointSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super().put(request, *args, **kwargs)
        else:
            return Response({"detail": "У вас нет прав на обновление этой точки."},
                            status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super().delete(request, *args, **kwargs)
        else:
            return Response({"detail": "У вас нет прав на удаление этой точки."},
                            status=status.HTTP_403_FORBIDDEN)


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
            return Response({"error": f"Вы слишком далеко от точки. Расстояние: {distance:.2f} метров"},
                            status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            visit, created = VisitedPoint.objects.get_or_create(user=user, point=point)
            if not created:
                return Response({"message": "Вы уже отмечались в этой точке"}, status=status.HTTP_200_OK)

            user.level += point.exp // 100
            user.save()

        return Response({"message": "Вы успешно отметились!", "new_level": user.level}, status=status.HTTP_200_OK)


class ArticleDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super().put(request, *args, **kwargs)
        else:
            return Response({"detail": "У вас нет прав на обновление этой статьи."},
                            status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super().patch(request, *args, **kwargs)
        else:
            return Response({"detail": "У вас нет прав на обновление этой статьи."},
                            status=status.HTTP_403_FORBIDDEN)

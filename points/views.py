from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Category, Point
from .serializers import CategorySerializer, PointSerializer
from drf_yasg.utils import swagger_auto_schema


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

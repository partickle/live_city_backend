from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserPoint
from .serializers import UserPointSerializer
from drf_yasg.utils import swagger_auto_schema


class UserPointCreateAPIView(generics.CreateAPIView):
    queryset = UserPoint.objects.all()
    serializer_class = UserPointSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserPointModerationAPIView(generics.UpdateAPIView):
    queryset = UserPoint.objects.all()
    serializer_class = UserPointSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Moderate a user point (activate/deactivate)",
        responses={200: UserPointSerializer, 403: "Forbidden"}
    )
    def patch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"detail": "You do not have permission to moderate points."},
                            status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        instance.is_active = request.data.get('is_active', instance.is_active)
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UserPointListAPIView(generics.ListAPIView):
    queryset = UserPoint.objects.all()
    serializer_class = UserPointSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a list of user points filtered by active status",
        responses={200: UserPointSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        now = timezone.now()
        UserPoint.objects.filter(end_time__lt=now).delete()
        is_active = request.query_params.get('is_active', None)
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = UserPoint.objects.filter(is_active=is_active)
        else:
            queryset = UserPoint.objects.all()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from LiveCity import settings
from .models import User
from .serializers import (LoginSerializer, ResetPasswordSerializer, SendVerificationCodeSerializer,
                          VerifyVerificationCodeSerializer, MyUserSerializer, UserBlockSerializer)
from rest_framework import generics, status
from rest_framework.views import APIView
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
import cachetools
import random
import string
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from django.urls import reverse

cache = cachetools.TTLCache(maxsize=100, ttl=600)


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        user_data = MyUserSerializer(user, context={'request': request}).data

        profile_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "experience": user.experience,
            "level": user.level,
            "email": user.email,
        }

        user_profile = {**user_data, **profile_data}

        return Response(user_profile, status=status.HTTP_200_OK)


class VerifyAccountView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(user_id=user_id, is_active=False)
            user.is_active = True
            user.save()
            return Response({"message": "Account activated successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Invalid or expired link"}, status=status.HTTP_404_NOT_FOUND)


class RegisterAPIView(generics.GenericAPIView):
    serializer_class = MyUserSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        user_data = MyUserSerializer(user, context={'request': request}).data

        self.send_activation_email(user, request)

        return Response({
            "user": user_data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "User Registered. Activation email sent. Please activate your account."
        }, status=status.HTTP_201_CREATED)

    def send_activation_email(self, user, request):
        activation_link = request.build_absolute_uri(reverse('verify-activation', args=[user.user_id]))
        context = {
            'user': user,
            'activation_link': activation_link
        }
        html_content = render_to_string("activation_email.html", context)
        text_content = strip_tags(html_content)

        email_message = EmailMultiAlternatives(
            'Activate Your Account',
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()


class LoginAPIView(generics.GenericAPIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, username=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": MyUserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "message": "User Logged In Successfully."
            }, status=status.HTTP_200_OK)
        return Response({"message": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class SendVerificationCodeView(APIView):
    @swagger_auto_schema(request_body=SendVerificationCodeSerializer)
    def post(self, request, *args, **kwargs):
        serializer = SendVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        code = ''.join(random.choice(string.digits) for _ in range(6))
        cache[user.email] = code

        context = {'code': code, 'user': user}
        html_content = render_to_string('verification_email.html', context)
        text_content = strip_tags(html_content)

        email_message = EmailMultiAlternatives(
            'Your Activation Code',
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [email]
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()

        return Response({"message": "Verification code sent to email"}, status=status.HTTP_200_OK)


class VerifyVerificationCodeView(APIView):
    @swagger_auto_schema(request_body=VerifyVerificationCodeSerializer)
    def post(self, request, *args, **kwargs):
        serializer = VerifyVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        if email not in cache:
            return Response({"error": "Verification code has expired."}, status=status.HTTP_400_BAD_REQUEST)
        if cache[email] != code:
            return Response({"error": "Invalid verification code."}, status=status.HTTP_400_BAD_REQUEST)

        del cache[email]
        return Response({"message": "Verification code is valid."}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    @swagger_auto_schema(request_body=ResetPasswordSerializer)
    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()

        if email in cache:
            del cache[email]

        return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.user.delete()
        return Response({"message": "Account deleted successfully."}, status=status.HTTP_200_OK)


class AdminLoginAPIView(generics.GenericAPIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, username=email, password=password)

        if user and user.is_staff:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        return Response({"message": "Invalid Credentials or Not an Admin"}, status=status.HTTP_401_UNAUTHORIZED)


class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserBlockSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"detail": "You do not have permission to view this page."},
                            status=status.HTTP_403_FORBIDDEN)
        return super().get(request, *args, **kwargs)


class UserDeactivateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: "User deactivated", 403: "Permission denied", 404: "User not found"}
    )
    def post(self, request, user_id, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = False
        user.save()
        return Response({"message": f"User {user.username} deactivated successfully."},
                        status=status.HTTP_200_OK)

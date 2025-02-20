from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from LiveCity import settings
from .models import User
from .serializers import (LoginSerializer, ResetPasswordSerializer, SendVerificationCodeSerializer,
                          VerifyVerificationCodeSerializer, MyUserSerializer)
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

cache = cachetools.TTLCache(maxsize=100, ttl=600)


class RegisterAPIView(generics.GenericAPIView):
    serializer_class = MyUserSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": MyUserSerializer(user).data,
                "message": "User Created Successfully."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            return Response({"message": "Admin Logged In Successfully."}, status=status.HTTP_200_OK)

        return Response({"message": "Invalid Credentials or Not an Admin"}, status=status.HTTP_401_UNAUTHORIZED)

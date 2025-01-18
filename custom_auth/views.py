from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated


class RegisterView(APIView):
    def post(self, request):
        # Extract data from the request
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        # Check if all fields are provided
        if not username:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Username is required",
                "contents": None
            }, status=status.HTTP_400_BAD_REQUEST)

        if not email:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Email is required",
                "contents": None
            }, status=status.HTTP_400_BAD_REQUEST)

        if not password:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Password is required",
                "contents": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Username already exists",
                "contents": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Email already exists",
                "contents": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create the user
        user = User.objects.create_user(
            username=username, email=email, password=password)
        user.save()

        return Response({
            "status": status.HTTP_200_OK,
            "message": "User registered successfully",
            "contents": None
        }, status=status.HTTP_200_OK)


class LoginView(APIView):
    def post(self, request):
        # Extract data from the request
        username = request.data.get('username')
        password = request.data.get('password')

        # Check if all fields are provided
        if not username:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Username is required",
                "contents": None
            }, status=status.HTTP_400_BAD_REQUEST)

        if not password:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Password is required",
                "contents": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user
        user = authenticate(username=username, password=password)
        if user is not None:
            # Generate or retrieve the token
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "status": status.HTTP_200_OK,
                "message": "Login successful",
                "contents": {
                    "token": token.key,
                    "is_superuser": user.is_superuser
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Invalid credentials",
                "contents": None
            }, status=status.HTTP_401_UNAUTHORIZED)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Mengambil pengguna yang sedang login
        profile_data = {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_superuser": user.is_superuser

        }

        return Response({
            "status": status.HTTP_200_OK,
            "message": "Profile retrieved successfully",
            "contents": profile_data,
        }, status=status.HTTP_200_OK)

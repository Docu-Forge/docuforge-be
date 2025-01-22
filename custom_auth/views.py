from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from docusign_esign import ApiClient, ApiException
from django.conf import settings
import uuid


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


class CodeGrantAuthView(APIView):
    """
    Starting authorization by code grant
    """

    def get(self, request):
        try:
            # Inisialisasi klien DocuSign
            api_client = ApiClient()
            api_client.set_base_path(settings.DOCUSIGN['AUTH_SERVER'])

            # Buat URL untuk otorisasi Code Grant
            url = api_client.get_authorization_uri(
                client_id=settings.DOCUSIGN['CLIENT_ID'],
                scopes=["signature", "impersonation"],  # Scope yang diperlukan
                redirect_uri=settings.DOCUSIGN['REDIRECT_URI'],
                response_type="code",
                state=uuid.uuid4().hex.upper()
            )
            print("Sukses")
            return Response({
                "reason": "Unauthorized",
                "response": "Permissions should be granted for current integration",
                "url": url
            }, status=status.HTTP_401_UNAUTHORIZED)
        except ApiException as exc:
            # Tangani error dari DocuSign SDK
            return Response({
                "reason": "Error occurred during authentication",
                "response": str(exc)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CallbackView(APIView):
    """
    Handle callback from frontend with authorization code
    """

    def post(self, request):
        # Ambil kode dari body permintaan
        code = request.data.get("code")

        if not code:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Authorization code is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            api_client = ApiClient()
            response = api_client.generate_access_token(
                client_id=settings.DOCUSIGN['CLIENT_ID'],
                client_secret=settings.DOCUSIGN['CLIENT_SECRET'],
                code=code
            )

            print('response1 : ', response)

            api_client.set_default_header(
                header_name="Authorization",
                header_value=f"Bearer {response.access_token}"
            )
            api_client.host = settings.DOCUSIGN['AUTH_SERVER']
            account_response = api_client.call_api(
                '/oauth/userinfo', 'GET', response_type='object'
            )
            print('response2 : ', account_response)

            if len(account_response) > 1 and 300 > account_response[1] > 200:
                raise Exception(f'Cannot get user info: {account_response[1]}')

            accounts = account_response[0]['accounts']
            target = settings.DOCUSIGN['TARGET_ACCOUNT_ID']

            account_info = None
            # Look for specific account
            if target is not None and target != 'FALSE':
                for acc in accounts:
                    if acc['account_id'] == target:
                        account_info = acc

                raise Exception(
                    f'\n\nUser does not have access to account {target}\n\n')

            # Look for default
            for acc in accounts:
                if acc['is_default']:
                    account_info = acc
            auth_data = {
                'access_token': response.access_token,
                'refresh_token': response.refresh_token,
                'account_info': account_response[0],
                'expires_in': int(response.expires_in),
                'auth_type': 'code_grant'
            }

            if account_response[1] == 200:
                return Response({
                    "status": status.HTTP_200_OK,
                    "message": "Callback handled successfully",
                    "contents": auth_data  # Token atau data lainnya
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Failed to exchange authorization code",
                    "error": account_response.json()
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An error occurred while processing the callback",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserinfoView(APIView):
    """
    View untuk mengambil informasi pengguna dari DocuSign
    """

    def get(self, request):
        try:
            # Inisialisasi DocuSign API Client
            api_client = ApiClient()
            api_client.set_base_path(settings.DOCUSIGN['BASE_URL'])

            # Ambil token akses dari header permintaan
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return Response({
                    "status": status.HTTP_401_UNAUTHORIZED,
                    "message": "Authorization token is required",
                }, status=status.HTTP_401_UNAUTHORIZED)

            # Pastikan token tidak mengandung "Bearer "
            access_token = auth_header.split(
                " ")[1] if " " in auth_header else auth_header

            # Set token akses sebagai header default
            api_client.set_default_header(
                header_name="Authorization",
                header_value=f"Bearer {access_token}",
            )
            api_client.host = settings.DOCUSIGN['AUTH_SERVER']

            # Panggil endpoint UserInfo dari DocuSign
            response = api_client.call_api(
                '/oauth/userinfo', 'GET', response_type='object'
            )

            return Response({
                "status": status.HTTP_200_OK,
                "message": "User information retrieved successfully",
                "contents": response[0]
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Failed to retrieve user information",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

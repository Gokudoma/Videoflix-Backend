import django_rq

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import LoginSerializer, PasswordResetSerializer, RegistrationSerializer, SetNewPasswordSerializer
from .utils import account_activation_token
from ..models import CustomUser
from ..tasks import send_activation_email, send_password_reset_email


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    
    Creates a new user, generates an activation token, and enqueues an email task.
    """
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate Token and UID using the custom generator
        token = account_activation_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Construct Activation URL dynamically
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5500')
        activation_link = f"{frontend_url}/pages/auth/activate.html?uid={uid}&token={token}"

        # Offload email sending to the RQ Worker
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(send_activation_email, user.email, activation_link)

        response_data = {
            "user": {
                "id": user.id,
                "email": user.email
            },
            "token": token
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class ActivateAccountView(generics.GenericAPIView):
    """
    API endpoint to activate a user account via email token.
    """
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        # Check token using the custom generator
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Account successfully activated."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Activation link is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    """
    API endpoint for user login.
    Returns JWT tokens in HttpOnly cookies and user info in body.
    """
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Generate Tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            response_data = {
                "detail": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.email
                }
            }

            response = Response(response_data, status=status.HTTP_200_OK)

            # Set HttpOnly Cookies
            response.set_cookie(
                'access_token', 
                access_token, 
                httponly=True, 
                samesite='Lax'
            )
            response.set_cookie(
                'refresh_token', 
                str(refresh), 
                httponly=True, 
                samesite='Lax'
            )

            return response
        
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(views.APIView):
    """
    API endpoint for user logout.
    
    It invalidates the refresh token (blacklisting) and removes the authentication cookies.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            response = Response(
                {"detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."},
                status=status.HTTP_200_OK
            )

            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            
            return response

        except Exception as e:
            return Response({"error": "Refresh token is missing or invalid."}, status=status.HTTP_400_BAD_REQUEST)


class CookieTokenRefreshView(TokenRefreshView):
    """
    API endpoint to refresh the access token using the refresh token from the cookie.
    """
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response({"detail": "Refresh token is missing."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={'refresh': refresh_token})
        
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        token_data = serializer.validated_data
        access_token = token_data.get('access')

        response_data = {
            "detail": "Token refreshed",
            "access": access_token
        }
        response = Response(response_data, status=status.HTTP_200_OK)

        response.set_cookie(
            'access_token',
            access_token,
            httponly=True,
            samesite='Lax'
        )
        
        return response


class PasswordResetView(generics.GenericAPIView):
    """
    API endpoint to request a password reset email.
    
    If the email exists, a reset link containing a token is sent to the user.
    """
    serializer_class = PasswordResetSerializer
    permission_classes = [] # Allow any user to request a reset

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            user = CustomUser.objects.get(email=email)
            # Generate token and uid
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Construct reset link dynamically
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5500')
            reset_link = f"{frontend_url}/reset-password/{uid}/{token}"

            # Offload email sending
            queue = django_rq.get_queue('default', autocommit=True)
            queue.enqueue(send_password_reset_email, user.email, reset_link)
            
        except CustomUser.DoesNotExist:
            # We return 200 even if the user does not exist to prevent email enumeration
            pass

        return Response({"detail": "An email has been sent to reset your password."}, status=status.HTTP_200_OK)
    

class PasswordResetConfirmView(generics.GenericAPIView):
    """
    API endpoint to set a new password.
    
    Validates the uid and token from the email link.
    If valid, sets the new password for the user.
    """
    serializer_class = SetNewPasswordSerializer
    permission_classes = [] # Allow any user (link contains the auth proof)

    def post(self, request, uidb64, token):
        try:
            # Decode the user ID
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return Response({'error': 'Invalid link.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the token is valid for this user
        if user is not None and default_token_generator.check_token(user, token):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Set the new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"detail": "Your Password has been successfully reset."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Link is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)
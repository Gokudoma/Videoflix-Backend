from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import django_rq

from .serializers import RegistrationSerializer, LoginSerializer
from ..models import CustomUser
from ..tasks import send_activation_email

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

        # Generate Token and UID
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Construct Activation URL (Pointing to Backend API as requested)
        # Note: In a real frontend app, this might point to an Angular route.
        # But here we stick to the backend URL structure.
        activation_link = f"http://localhost:8000/api/activate/{uid}/{token}/"

        # Offload email sending to the RQ Worker
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(send_activation_email, user.email, activation_link)

        # Construct response exactly as specified in the docs
        response_data = {
            "user": {
                "id": user.id,
                "email": user.email
            },
            "token": token # Just for demo purposes as per docs
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

        if user is not None and default_token_generator.check_token(user, token):
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

        # Authenticate user (email is mapped to username in our CustomUser)
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Generate Tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            # Response Data (matches screenshot requirements)
            response_data = {
                "detail": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.email  # Map email to 'username' key as per docs
                }
            }

            response = Response(response_data, status=status.HTTP_200_OK)

            # Set HttpOnly Cookies (Secure flag commented out for localhost dev)
            response.set_cookie(
                'access_token', 
                access_token, 
                httponly=True, 
                samesite='Lax'
                # secure=True # Uncomment in production with HTTPS
            )
            response.set_cookie(
                'refresh_token', 
                str(refresh), 
                httponly=True, 
                samesite='Lax'
            )

            return response
        
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
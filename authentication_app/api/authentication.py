from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom Authentication class to read JWT from HttpOnly cookies.
    """
    def authenticate(self, request):
        # Try to get the access token from the cookie
        header = self.get_header(request)
        
        if header is None:
            raw_token = request.COOKIES.get('access_token')
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except AuthenticationFailed:
            return None

        return self.get_user(validated_token), validated_token
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Allow clients to send {"email": "...", "password": "..."}.
    We'll map "email" to the username_field that Django expects.
    """
    def validate(self, attrs):
        if 'email' in attrs and 'username' not in attrs:
            # DRF SimpleJWT uses `username` internally; map email->username
            attrs['username'] = attrs['email']
        return super().validate(attrs)

class EmailTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = EmailTokenObtainPairSerializer

class UsersMeView(APIView):
    """
    Minimal /api/users/me returning the authenticated user.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({
            "id": getattr(u, "id", None),
            "email": getattr(u, "email", ""),
            "username": getattr(u, "username", ""),
            "is_staff": getattr(u, "is_staff", False),
            "is_superuser": getattr(u, "is_superuser", False),
        })

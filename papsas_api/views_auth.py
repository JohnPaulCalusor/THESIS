from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from papsas_app.analytics.audit import log_event

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
    throttle_scope = "auth_login"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        payload = request.data or {}
        username = payload.get("username") or payload.get("email") or ""
        is_success = response.status_code == status.HTTP_200_OK
        action = "AUTH_LOGIN_SUCCESS" if is_success else "AUTH_LOGIN_FAILURE"
        status_label = "success" if is_success else "error"
        try:
            log_event(
                request,
                action=action,
                status=status_label,
                target_type="auth",
                target_id=username,
                meta={"status_code": response.status_code},
                payload_for_hash={"username": username, "status_code": response.status_code},
            )
        except Exception:
            pass
        return response

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

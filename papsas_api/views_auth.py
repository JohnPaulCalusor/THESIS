from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from papsas_app.analytics.audit import log_event

User = get_user_model()

NO_ACTIVE_ACCOUNT_MESSAGE = TokenObtainPairSerializer.default_error_messages["no_active_account"]


def _resolve_login_identifier(identifier):
    identifier = (identifier or "").strip()
    if not identifier:
        return identifier
    user_qs = User.objects.filter(
        Q(username__iexact=identifier) | Q(email__iexact=identifier)
    )
    if not user_qs.exists():
        return identifier
    user_obj = user_qs.order_by("id").first()
    return user_obj.username or identifier

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
        payload = request.data or {}
        identifier = (payload.get("username") or payload.get("email") or "").strip()
        password = payload.get("password") or ""
        resolved_username = _resolve_login_identifier(identifier)
        user = authenticate(request, username=resolved_username, password=password)
        if user is None or not getattr(user, "is_active", True):
            raise AuthenticationFailed(NO_ACTIVE_ACCOUNT_MESSAGE)
        serializer_data = payload.copy()
        serializer_data["username"] = resolved_username
        serializer_data["password"] = password
        serializer = self.get_serializer(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        username_for_log = identifier or ""
        is_success = response.status_code == status.HTTP_200_OK
        action = "AUTH_LOGIN_SUCCESS" if is_success else "AUTH_LOGIN_FAILURE"
        status_label = "success" if is_success else "error"
        try:
            log_event(
                request,
                action=action,
                status=status_label,
                target_type="auth",
                target_id=username_for_log,
                meta={"status_code": response.status_code},
                payload_for_hash={"username": username_for_log, "status_code": response.status_code},
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

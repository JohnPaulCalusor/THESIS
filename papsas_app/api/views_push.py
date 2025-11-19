from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging

from papsas_app.models import DevicePushToken

logger = logging.getLogger(__name__)

VALID_PLATFORMS = ("android", "ios")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_push_token(request):
    """
    Upsert the current user's Expo push token.

    Request JSON:
      {
        "token": "ExponentPushToken[xxxxxxxxxxxxxx]",
        "platform": "android" | "ios"
      }

    Response (200):
      {
        "code": "push_token_registered",
        "message": "Push token registered.",
        "data": {
          "id": <int>,
          "platform": "android" | "ios",
          "created": true | false
        }
      }
    """
    user = request.user
    data = request.data or {}

    logger.info(
        "register_push_token: user=%s authenticated=%s data=%r",
        getattr(user, "id", None),
        getattr(user, "is_authenticated", False),
        data,
    )

    raw_token = data.get("token") or ""
    token = str(raw_token).strip()
    platform = str(data.get("platform") or "").strip().lower()

    if not token:
        return Response(
            {
                "code": "push_token_missing",
                "message": "Push token is required.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if platform not in VALID_PLATFORMS:
        return Response(
            {
                "code": "push_platform_invalid",
                "message": "Platform must be 'android' or 'ios'.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    defaults = {
        "user": user,
        "platform": platform,
        "is_active": True,
    }
    if hasattr(DevicePushToken, "updated_at"):
        defaults["updated_at"] = timezone.now()

    obj, created = DevicePushToken.objects.update_or_create(
        token=token,
        defaults=defaults,
    )

    return Response(
        {
            "code": "push_token_registered",
            "message": "Push token registered.",
            "data": {
                "id": obj.id,
                "platform": obj.platform,
                "created": created,
            },
        },
        status=status.HTTP_200_OK,
    )

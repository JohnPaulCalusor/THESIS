from django.contrib.auth import get_user_model, authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

User = get_user_model()

def issue_tokens(user):
    r = RefreshToken.for_user(user)
    return {"accessToken": str(r.access_token), "refreshToken": str(r)}

@api_view(["GET"])
@permission_classes([AllowAny])
def health(_req):
    return Response({"ok": True})

@api_view(["POST"])
@permission_classes([AllowAny])
def register(req):
    d = req.data
    need = ["firstName","lastName","email","password"]
    if not all(d.get(k) for k in need):
        return Response({"message":"Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

    email = (d.get("email") or "").strip().lower()
    if User.objects.filter(email=email).exists():
        return Response({"message":"Email already exists"}, status=status.HTTP_409_CONFLICT)

    user = User.objects.create_user(
        username=email, email=email, password=d["password"],
        first_name=d["firstName"], last_name=d.get("lastName") or d.get("LastName","")
    )
    t = issue_tokens(user)
    return Response({
        "accessToken": t["accessToken"], "refreshToken": t["refreshToken"],
        "user": {"id": user.id, "firstName": user.first_name, "lastName": user.last_name,
                 "email": user.email, "role": "member", "is_active": user.is_active,
                 "emailVerified": False}
    }, status=status.HTTP_201_CREATED)

@api_view(["POST"])
@permission_classes([AllowAny])
def login(req):
    email = (req.data.get("email") or "").strip().lower()
    password = req.data.get("password")
    if not email or not password:
        return Response({"message":"Missing credentials"}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=email, password=password)
    if not user or not user.is_active:
        return Response({"message":"Invalid credentials or inactive account"}, status=status.HTTP_401_UNAUTHORIZED)

    t = issue_tokens(user)
    return Response({
        "accessToken": t["accessToken"], "refreshToken": t["refreshToken"],
        "user": {"id": user.id, "firstName": user.first_name, "lastName": user.last_name,
                 "email": user.email, "role": "member", "is_active": user.is_active,
                 "emailVerified": False}
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(req):
    u = req.user
    return Response({"id": u.id, "firstName": u.first_name, "lastName": u.last_name,
                     "email": u.email, "role": "member", "is_active": u.is_active,
                     "emailVerified": False})

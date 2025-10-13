from rest_framework.permissions import BasePermission
class IsOfficer(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated: return False
        return bool(getattr(u, "is_officer", False) or getattr(u, "is_staff", False) or getattr(u, "is_superuser", False))

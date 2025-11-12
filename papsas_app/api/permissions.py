from rest_framework.permissions import BasePermission, SAFE_METHODS

from papsas_app.models import UserSecurity

def _is_admin(u):
    return bool(u.is_staff or u.groups.filter(name='admin').exists())

def _is_officer(u):
    return bool(u.groups.filter(name='officer').exists())

class IsAdminOrOfficer(BasePermission):
    """
    Allow Django staff OR users in the 'officer' group.
    """
    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated:
            return False
        if getattr(u, "is_staff", False):
            return True
        try:
            return u.groups.filter(name="officer").exists()
        except Exception:
            return False

class IsOfficer(BasePermission):
    """Legacy shim: allow access to officers and admins."""
    def has_permission(self, request, view):
        u = getattr(request, "user", None)
        return bool(u and u.is_authenticated and (_is_admin(u) or _is_officer(u)))

class IsAdminWrite(BasePermission):
    def has_permission(self, request, view):
        u = getattr(request, "user", None)
        if not (u and u.is_authenticated):
            return False
        if request.method in ('POST','PUT','PATCH','DELETE'):
            return _is_admin(u)
        return True

class IsOfficerOrAdminRead(BasePermission):
    def has_permission(self, request, view):
        u = getattr(request, "user", None)
        if not (u and u.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return bool(_is_admin(u) or _is_officer(u))
        return True

# New explicit permissions
class IsAdminOnly(BasePermission):
    def has_permission(self, request, view):
        u = getattr(request, "user", None)
        return bool(u and u.is_authenticated and _is_admin(u))

class IsOfficerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        u = getattr(request, "user", None)
        return bool(u and u.is_authenticated and (_is_admin(u) or _is_officer(u)))


class IsEmailVerified(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not (user and user.is_authenticated and user.email_verified):
            return False
        try:
            security = user.security
        except UserSecurity.DoesNotExist:
            return False
        return bool(getattr(security, "email_verified_at", None))

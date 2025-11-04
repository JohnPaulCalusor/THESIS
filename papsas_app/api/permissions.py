from rest_framework.permissions import BasePermission, SAFE_METHODS

def _is_admin(u):
    return bool(u.is_staff or u.groups.filter(name='admin').exists())

def _is_officer(u):
    return bool(u.groups.filter(name='officer').exists())

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

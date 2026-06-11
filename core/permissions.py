from rest_framework.permissions import BasePermission


class IsAdminOrReadOwnData(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or getattr(request.user, "role", None) == "admin":
            return True
        return getattr(obj, "user_id", None) == request.user.id or getattr(obj, "recipient_id", None) == request.user.id


class IsAdminOrAuthenticatedReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or getattr(request.user, "role", None) == "admin"
        )
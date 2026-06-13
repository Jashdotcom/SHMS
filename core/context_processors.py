from .models import Notification


def _is_admin_user(user):
    role = (getattr(user, "role", "") or "").strip().lower()
    return bool(user and user.is_authenticated and (user.is_superuser or role == "admin"))


def notification_context(request):
    if not request.user.is_authenticated:
        return {"recent_notifications": [], "unread_notification_count": 0, "is_admin_user": False}

    notifications = Notification.objects.filter(recipient=request.user).only("title", "message", "created_at", "is_read", "related_url")[:5]
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return {
        "recent_notifications": notifications,
        "unread_notification_count": unread_count,
        "is_admin_user": _is_admin_user(request.user),
    }

# notifications/context_processors.py
from .models import Notification

def unread_notifications(request):
    if request.user.is_authenticated:
        return {
            'unread_notifications_count': Notification.objects.filter(
                recipient=request.user,
                is_seen=False
            ).count()
        }
    return {}
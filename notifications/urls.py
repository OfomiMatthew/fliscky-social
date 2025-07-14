from django.urls import path
from .views import show_notifications, mark_notifications_seen,delete_notification

urlpatterns = [
    path('notifications-list', show_notifications, name='notifications-list'),
    path('mark-seen/', mark_notifications_seen, name='mark-notifications-seen'),
    path('delete/<int:notification_id>/', delete_notification, name='delete_notification'),
]

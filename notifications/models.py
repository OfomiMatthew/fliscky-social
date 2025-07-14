from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
  NOTIFICATION_TYPES =(('like', 'Like'),
                       ('comment', 'Comment'),
                       ('follow', 'Follow'),
                      )
  post = models.ForeignKey('post.Post', on_delete=models.CASCADE, related_name='notifications_post',blank=True, null=True)
  sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_from_user')
  recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_to_user')
  notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
  text_preview = models.CharField(max_length=255, blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  is_seen = models.BooleanField(default=False)

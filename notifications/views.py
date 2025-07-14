from django.shortcuts import render,redirect
from .models import Notification
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Create your views here.
@login_required
def show_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    context = {
        'notifications': notifications
    }
    return render(request, 'notifications/notifications_list.html', context)
  


@login_required
def mark_notifications_seen(request):
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user, is_seen=False).update(is_seen=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
  
@login_required
def delete_notification(request, notification_id):
  user = request.user
  notification = Notification.objects.get(id=notification_id, recipient=user)
  notification.delete()
  return redirect('notifications-list')
 
  
  
    

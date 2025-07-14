from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from .models import Message
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import models 
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required
def inbox(request):
    user = request.user
    conversations = Message.get_messages(user=user)
    active_direct = request.GET.get('active_direct')
    directs = None
    
    if conversations:
        # Set first conversation as active if none selected
        if not active_direct:
            active_direct = conversations[0]['user'].username
            
        # Get all messages between current user and selected user
        other_user = get_object_or_404(User, username=active_direct)
        directs = Message.objects.filter(
            (models.Q(sender=user) & models.Q(recipient=other_user)) |
            (models.Q(sender=other_user) & models.Q(recipient=user))
        ).order_by('date')
        
        Message.objects.filter(recipient=user, sender=other_user, is_read=False).update(is_read=True)
        
        # Mark received messages as read
        # directs.filter(recipient=user, is_read=False).update(is_read=True)
        
        # Update unread count for active conversation
        for conv in conversations:
            if conv['user'].username == active_direct:
                conv['unread'] = 0
    
    context = {
        'conversations': conversations,
        'directs': directs,
        'active_direct': active_direct,
        'unread_total':sum(conv['unread'] for conv in conversations),
    }
    return render(request, 'direct_message/inbox.html', context)



@login_required
def send_direct(request):
    if request.method == 'POST':
        body = request.POST.get('body')
        to_username = request.POST.get('to_user')
        
        if not body or not to_username:
            messages.error(request, "Message cannot be empty")
            return redirect('inbox')
            
        recipient = get_object_or_404(User, username=to_username)
        
        if recipient == request.user:
            messages.error(request, "You cannot message yourself")
            return redirect('inbox')
            
        Message.send_message(request.user, recipient, body)
        messages.success(request, "Message sent!")
        
    return redirect('inbox')


@login_required
def search_users(request):
    query = request.GET.get('q', '')
    context ={}
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id)
        paginator = Paginator(users, 10)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)
        context = {
            'users': users_paginator,
           
        }
    return render(request, 'direct_message/search_users.html', context)


def check_direct(request):
    directs_count = 0
    if request.user.is_authenticated:
        directs_count = Message.objects.filter(
            user=request.user, is_read=False
        ).count()
    return {'directs_count': directs_count}
        
      
    

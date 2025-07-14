from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Story, StoryStream
from .forms import NewStoryForm
from datetime import datetime, timedelta
from django.utils import timezone
from post.models import Follow
from django.contrib.auth.models import User







# @login_required
# def new_story(request):
#     user = request.user
#     if request.method == 'POST':
#         form = NewStoryForm(request.POST, request.FILES)
#         if form.is_valid():
#             files = request.FILES.getlist('content')  # Get list of files
#             caption = form.cleaned_data.get('caption')
            
#             for file in files:
#                 # Create a new Story instance for each file
#                 story = Story(
#                     user=user,
#                     caption=caption,
#                     content=file
#                 )
#                 story.save()
                
#                 # Create StoryStream entries for followers
#                 followers = Follow.objects.filter(following=user)
#                 for follower in followers:
#                     StoryStream.objects.create(
#                         user=follower.follower,
#                         following=user,
#                         date=story.date_posted
#                     ).story.add(story)
            
#             return redirect('home')
#     else:
#         form = NewStoryForm()
#     return render(request, 'new_story.html', {'form': form})

@login_required
def new_story(request):
    user = request.user
    if request.method == 'POST':
        form = NewStoryForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('content')
            caption = form.cleaned_data.get('caption')
            
            stories = []
            for file in files:
                stories.append(Story(
                    user=user,
                    caption=caption,
                    content=file
                ))
            
            # Bulk create stories
            Story.objects.bulk_create(stories)
            
            return redirect('home')
    else:
        form = NewStoryForm()
    return render(request, 'new_story.html', {'form': form})

      
      

def view_story(request, user_id):
    """View all active stories for a specific user"""
    stories = Story.objects.filter(
        user__id=user_id,
        expired=False,
        date_posted__gte=timezone.now()-timedelta(hours=24)
    ).order_by('date_posted').select_related('user')
    
    if not stories.exists():
        context = {'username': get_object_or_404(User, id=user_id).username}
        return render(request, 'no_stories.html', context)
    
    return render(request, 'view_story.html', {
        'stories': stories,
        'story_user': stories.first().user  # The user who posted these stories
    })
   
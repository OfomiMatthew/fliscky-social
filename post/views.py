from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from .models import Post,Stream,Follow,Tag,Likes,Comment,PostProfileContent
from .forms import NewPostForm,CommentForm
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.models import User
from account.models import Profile
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.core.files.storage import FileSystemStorage
import os
from stories.models import Story, StoryStream
from django.utils import timezone
from datetime import timedelta






@login_required
def home(request):
    post_items = Post.objects.all().order_by('-date_posted')
    stories = StoryStream.objects.filter(user=request.user)
  
    
    
    # Get suggested users (users you don't follow)
    suggested_users = User.objects.exclude(
        id__in=request.user.following_users.values_list('following', flat=True)
    ).exclude(id=request.user.id).order_by('?')[:5]  # Random 5 users
    
    return render(request, 'home.html', {
        'post_items': post_items,
        'suggested_users': suggested_users,
        'stories': stories,
    })


# @login_required
# def new_post(request):
#   user = request.user.id 
#   tags_objs =[]
#   if request.method == 'POST':
#     form = NewPostForm(request.POST,request.FILES)
#     if form.is_valid():
#       content = form.cleaned_data.get('content')
#       caption = form.cleaned_data.get('caption')
#       tags_form = form.cleaned_data.get('tags')
      
#       tags_list = list(tags_form.split(','))
      
#       for tag in tags_list:
#         t,created = Tag.objects.get_or_create(title=tag)
#         tags_objs.append(t)
#       p,created = Post.objects.get_or_create(content=content,caption=caption,user_id=user)
#       p.tags.set(tags_objs)
#       p.save()
#       return redirect('home')
#   else:
#     form = NewPostForm()
#   return render(request,'new_post.html',{'form':form})

# @login_required
# @transaction.atomic
# def new_post(request):
#     if request.method == 'POST':
#         form = NewPostForm(request.POST, request.FILES)
#         if form.is_valid():
#             # Create the post first
#             post = Post.objects.create(
#                 caption=form.cleaned_data['caption'],
#                 user=request.user
#             )
            
#             # Handle content files
#             files = request.FILES.getlist('content')
#             for file in files:
#                 content = PostProfileContent.objects.create(
#                     user=request.user,
#                     file=file
#                 )
#                 post.content.add(content)
            
#             # Handle tags
#             tags_form = form.cleaned_data.get('tags', '')
#             tags_list = [tag.strip() for tag in tags_form.split(',') if tag.strip()]
#             tags_objs = []
#             for tag in tags_list:
#                 t, created = Tag.objects.get_or_create(title=tag)
#                 tags_objs.append(t)
#             post.tags.set(tags_objs)
            
#             return redirect('home')
#     else:
#         form = NewPostForm()
    
#     return render(request, 'new_post.html', {'form': form})

# @login_required
# def new_post(request):
#     if request.method == 'POST':
#         form = NewPostForm(request.POST,request.FILES)
#         if form.is_valid():
#             post = Post.objects.create(
#                 caption=form.cleaned_data['caption'],
#                 user=request.user
#             )
            
#             # Handle multiple files
#             for file in request.FILES.getlist('content'):
#                 content = PostProfileContent.objects.create(
#                     user=request.user,
#                     file=file
#                 )
#                 post.content.add(content)
            
#             # Handle tags
#             tags_form = form.cleaned_data.get('tags', '')
#             tags_list = [tag.strip() for tag in tags_form.split(',') if tag.strip()]
#             tags_objs = []
#             for tag in tags_list:
#                 t, created = Tag.objects.get_or_create(title=tag)
#                 tags_objs.append(t)
#             post.tags.set(tags_objs)
            
#             return redirect('home')
#     else:
#         form = NewPostForm()
    
#     return render(request, 'new_post.html', {'form': form})




@login_required
def new_post(request):
    if request.method == 'POST':
        try:
            # Get form data
            caption = request.POST.get('caption', '').strip()
            tags_str = request.POST.get('tags', '').strip()
            files = request.FILES.getlist('content')
            
            # Basic validation
            if not caption:
                messages.error(request, "Caption is required")
                return redirect('new_post')
                
            if not files:
                messages.error(request, "Please upload at least one file")
                return redirect('new_post')
            
            with transaction.atomic():
                # Create the post
                post = Post.objects.create(
                    caption=caption,
                    user=request.user
                )
                
                # Handle uploaded files
                for file in files:
                    # Validate file size
                    if file.size > 100 * 1024 * 1024:  # 100MB
                        messages.error(request, f"File {file.name} is too large (max 100MB)")
                        continue
                    
                    # Create content object
                    content = PostProfileContent.objects.create(
                        user=request.user,
                        file=file
                    )
                    post.content.add(content)
                
                # Handle tags
                if tags_str:
                    tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                    tags_objs = []
                    for tag in tags_list:
                        t, created = Tag.objects.get_or_create(title=tag)
                        tags_objs.append(t)
                    post.tags.set(tags_objs)
                
                messages.success(request, "Post created successfully!")
                return redirect('home')
                
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('new_post')
    
    # GET request - show empty form
    return render(request, 'new_post.html')










@login_required
def post_details(request,post_id):
  post = get_object_or_404(Post,id=post_id)
  return render(request,'post_detail.html',{'post':post})

@login_required
def get_tags(request,tag_slug):
  tags = get_object_or_404(Tag,slug=tag_slug)
  posts = Post.objects.filter(tags=tags).order_by('-date_posted')
  
  return render(request,'tags.html',{'posts':posts,'tags':tags})





@transaction.atomic
def like(request, username, post_id):
    try:
        user_liking = request.user
        user_post = get_object_or_404(User, username=username)
       
        # Corrected: Get post by UUID (post_id) instead of user
        post = get_object_or_404(Post, id=post_id)
        
        # Check if user already unliked (type_like=1)
        existing_unlike = Likes.objects.filter(user=user_liking, review=post, type_like=1).first()
        
        if existing_unlike:
            # Remove the unlike first
            existing_unlike.delete()
            post.unlikes -= 1
        
        # Check if already liked
        existing_like = Likes.objects.filter(user=user_liking, review=post, type_like=2).first()
        
        if existing_like:
            existing_like.delete()
            post.likes -= 1
            messages.info(request, "Like removed")
        else:
            Likes.objects.create(user=user_liking, review=post, type_like=2)
            post.likes += 1
            messages.success(request, "Post liked!")
        
        post.save()
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
    
    # Corrected: Use post_id parameter instead of id function
    return redirect('post_details', post_id=post_id)

@transaction.atomic
def unlike(request, username, post_id):
    try:
        user_unliking = request.user
        user_post = get_object_or_404(User, username=username)
     
        # Corrected: Get post by UUID (post_id) instead of user
        post = get_object_or_404(Post, id=post_id)
        
        # Check if user already liked (type_like=2)
        existing_like = Likes.objects.filter(user=user_unliking, review=post, type_like=2).first()
        
        if existing_like:
            # Remove the like first
            existing_like.delete()
            post.likes -= 1
        
        # Check if already unliked
        existing_unlike = Likes.objects.filter(user=user_unliking, review=post, type_like=1).first()
        
        if existing_unlike:
            existing_unlike.delete()
            post.unlikes -= 1
            messages.info(request, "Unlike removed")
        else:
            Likes.objects.create(user=user_unliking, review=post, type_like=1)
            post.unlikes += 1
            messages.warning(request, "Post unliked")
        
        post.save()
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
    
    # Corrected: Use post_id parameter instead of id function
    return redirect('post_details', post_id=post_id)
  
  



def add_comment(request, username, post_id):
    review_user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, user=review_user, id=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post  # Fix: Assign the post, not the text
            comment.user = request.user
            comment.save()
            messages.success(request, "Comment added successfully!")
            return redirect('post_details', post_id=post.id)  # Use correct URL name
    
    return redirect('post_details', post_id=post.id)
  
  
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    post_id = comment.post.id
    comment.delete()
    messages.success(request, "Comment deleted successfully!")
    return redirect('post_details', post_id=post_id)



def favorite_post(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
        profile = request.user.profile
        
        if post in profile.favorites.all():  # Changed to use 'in' instead of filter().exists()
            profile.favorites.remove(post)
            messages.info(request, "Removed from favorites")
        else:
            profile.favorites.add(post)
            messages.success(request, "Added to favorites!")
        
        return redirect('post_details', post_id=post_id)
    
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('post_details', post_id=post_id)
    

@login_required   
def favorites_lists(request):
    profile = get_object_or_404(Profile, user=request.user)
    favorites_post = profile.favorites.all()
    return render(request, 'favorites.html', {'favorites':favorites_post})



@login_required
def remove_from_favorites(request, post_id):
    try:
        # Get the current user's profile
        profile = get_object_or_404(Profile, user=request.user)
        
        # Get the post to remove
        post = get_object_or_404(Post, id=post_id)
        
        # Remove the post from favorites
        profile.favorites.remove(post)
        
        messages.success(request, "Post removed from your favorites")
    except Exception as e:
        messages.error(request, f"Error removing from favorites: {str(e)}")
    
    return redirect('favorites_lists')





User = get_user_model()

@login_required
def explore_users(request):
    # Get users not followed by current user, excluding self
    users_to_follow = User.objects.exclude(
        id__in=request.user.following_users.values_list('following', flat=True)
    ).exclude(id=request.user.id).order_by('?')  # Random order
    
    # Pagination (12 users per page)
    paginator = Paginator(users_to_follow, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'explore_users.html', {
        'page_obj': page_obj,
        'title': 'Discover People'
    })
    


        
        











    
    
    
    


    

    



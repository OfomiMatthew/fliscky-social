from django.shortcuts import render,redirect,get_object_or_404
from .forms import SignupForm,EditProfileForm
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash,logout
from .models import Profile
from django.contrib.auth.decorators import login_required
from post.models import Post,Follow,Stream
from django.db import transaction
from django.contrib import messages

# Create your views here.
def SignUp(request):
  if request.method == 'POST':
    form = SignupForm(request.POST)
    if form.is_valid():
      username = form.cleaned_data.get('username')
      email = form.cleaned_data.get('email')
      first_name = form.cleaned_data.get('first_name')
      last_name = form.cleaned_data.get('last_name')
      password = form.cleaned_data.get('password')
      User.objects.create_user(username=username,email=email,password=password,first_name=first_name,last_name=last_name)
      return redirect('login') #edit-profile page
  else:
    form = SignupForm()
  return render(request,'registration/signup.html',{'form':form})


def logout_view(request):
  logout(request)
  return redirect('login')




@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    posts = Post.objects.filter(user=user).order_by('-date_posted')
    
    # Check if current user follows this profile
    is_following = Follow.objects.filter(
        follower=request.user, 
        following=user
    ).exists()
    
    # Get follower/following counts
    follower_count = Follow.objects.filter(following=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    
    return render(request, 'registration/profile.html', {
        'posts': posts,
        'profile': profile,
        'user': user,
        'is_following': is_following,
        'follower_count': follower_count,
        'following_count': following_count,
        'active_tab': 'posts'
    })

@login_required
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile',username=request.user.username)
    else:
        form = EditProfileForm(instance=profile)
        
    return render(request, 'registration/edit-profile.html', {'form': form,'profile':profile})
  
  



@login_required 
def follow(request, username, option):
    user = request.user
    target_user = get_object_or_404(User, username=username)
    
    # Prevent users from following themselves
    if user == target_user:
        messages.warning(request, "You cannot follow yourself")
        return redirect('profile', username)
    
    try:
        if int(option) == 1:  # Follow action
            # Check if follow relationship already exists
            if not Follow.objects.filter(follower=user, following=target_user).exists():
                Follow.objects.create(follower=user, following=target_user)
                messages.success(request, f"You are now following {target_user.username}")
                
                # Add to stream
                posts = Post.objects.filter(user=target_user)[:10]
                with transaction.atomic():
                    for post in posts:
                        Stream.objects.create(
                            post=post,
                            user=user,
                            date=post.date_posted,
                            following=target_user
                        )
        else:  # Unfollow action (option == 0)
            Follow.objects.filter(follower=user, following=target_user).delete()
            Stream.objects.filter(following=target_user, user=user).delete()
            messages.info(request, f"You unfollowed {target_user.username}")
            
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
    
    return redirect('profile', username)
  
 
 
  
@login_required
def followers_list(request, username):
    user = get_object_or_404(User, username=username)
    # Users who follow the current profile
    followers = User.objects.filter(following_users__following=user)
    return render(request, 'followers.html', {
        'user': user,
        'followers': followers,
        'profile': user.profile,
        'is_following': lambda u: Follow.objects.filter(
            follower=request.user, 
            following=u
        ).exists()
    })

@login_required
def following_list(request, username):
    user = get_object_or_404(User, username=username)
    # Users that the current profile follows
    following = User.objects.filter(follower_users__follower=user)
    return render(request, 'following.html', {
        'user': user,
        'following': following,
        'profile': user.profile,
        'is_following': lambda u: Follow.objects.filter(
            follower=request.user, 
            following=u
        ).exists()
    })
  
  

# # followers_list view
# @login_required
# def followers_list(request, username):
#     user = get_object_or_404(User, username=username)
#     followers = User.objects.filter(following__following=user)
#     return render(request, 'followers.html', {
#         'user': user,
#         'followers': followers,
#         'profile': user.profile
#     })

# # following_list view
# @login_required
# def following_list(request, username):
#     user = get_object_or_404(User, username=username)
#     following = User.objects.filter(follower__follower=user)
#     return render(request, 'following.html', {
#         'user': user,
#         'following': following,
#         'profile': user.profile
#     })
    
          
      
    

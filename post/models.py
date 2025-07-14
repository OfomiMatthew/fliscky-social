from django.db import models
from django.contrib.auth.models import User 
from django.utils.text import slugify
from django.db.models.signals import post_save,pre_delete,post_delete
import os 
from django.conf import settings 
from django.urls import reverse
import uuid
from django.dispatch import receiver
from notifications.models import Notification



# Function to generate a unique file path for user-uploaded images
def user_directory_path(instance,filename):
  ext = filename.split('.')[-1]  # Get file extension
  unique_id = uuid.uuid4().hex[:6]  # Generate unique identifier
  new_filename = f'user_{instance.user.id}/post_{unique_id}.{ext}'
  return new_filename


class Tag(models.Model):
  title = models.CharField(max_length=100,verbose_name='Tag')
  slug = models.SlugField(null=False,unique=True)
  
  class Meta:
    verbose_name_plural ='Tags'
    
  def get_absolute_url(self):
    return reverse('tags',arg=[self.slug])
  
  def __str__(self):
    return self.title
  
  def save(self,*args,**kwargs):
    if not self.slug:
      self.slug = slugify(self.title)
    return super().save(*args,**kwargs)
  
  


class PostProfileContent(models.Model):
    CONTENT_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_owner')
    file = models.FileField(upload_to='post_content', verbose_name='File', null=True, blank=True)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES, default='image')
    
    def save(self, *args, **kwargs):
        # Auto-detect content type based on file extension
        ext = os.path.splitext(self.file.name)[1].lower()
        if ext in ['.mp4', '.mov', '.avi', '.mkv']:
            self.content_type = 'video'
        super().save(*args, **kwargs)
  
  
class Post(models.Model):
  id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
  content = models.ManyToManyField(PostProfileContent,related_name='contents',blank=True)
  caption = models.TextField(max_length=2000,verbose_name='caption')
  date_posted = models.DateTimeField(auto_now_add=True)
  tags = models.ManyToManyField(Tag,related_name='tags')
  user = models.ForeignKey(User,on_delete=models.CASCADE)
  likes = models.IntegerField(default=0)
  unlikes = models.IntegerField(default=0)
  
  def get_absolute_url(self):
    return reverse('post-details',args=[str(self.id)])
  
  
  @property
  def likers(self):
    return User.objects.filter(likes__review=self, likes__type_like=2)
    
  @property
  def unlikers(self):
    return User.objects.filter(likes__review=self, likes__type_like=1)
  
  def __str__(self):
    return f'Posted by: {self.user.username} - {str(self.date_posted)} - {self.id} ' 
  
class Likes(models.Model):
  user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_like')
  type_like = models.PositiveSmallIntegerField()
  review = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='post_like')
  
  
  def user_liked_post(sender,instance,*args,**kwargs):
    like = instance
    post = like.review
    sender = like.user
    notify =Notification(post=post,sender=sender,recipient=post.user,notification_type='like',text_preview=f'{sender.username} liked your post')
    notify.save()
  
 
   
  


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_users')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_users')
    
    class Meta:
        unique_together = ('follower', 'following')  # Prevent duplicate follows
    
    def __str__(self):
        return f'{self.follower} follows {self.following}'
      
    def user_follow(sender, instance, *args, **kwargs):
        follow = instance
        sender = follow.follower
        following = follow.following
        
        # Create a notification for the user being followed
        notify = Notification(
            sender=sender,
            recipient=following,
            notification_type='follow',
            
        )
        notify.save()
    def user_unfollow(sender, instance, *args, **kwargs):
        follow = instance
        sender = follow.follower
        following = follow.following
        
        # Delete the notification for the user being unfollowed
        notify = Notification.objects.filter(
            sender=sender,
            recipient=following,
            notification_type='follow'
        )
        if notify.exists():
            notify.delete()
  
class Stream(models.Model):
  following = models.ForeignKey(User,on_delete=models.CASCADE,related_name='stream_following')
  user = models.ForeignKey(User,on_delete=models.CASCADE)
  post = models.ForeignKey(Post,on_delete=models.CASCADE)
  date = models.DateTimeField()
  
  
  def __str__(self):
    return f'Stream: {self.user} is following {self.following}'
  
  def add_post(sender,instance,*args,**kwargs):
    post = instance 
    user = post.user
    followers = Follow.objects.all().filter(following=user) #filter all users (following) that are following you (user)
    
    for follower in followers:
      stream = Stream.objects.create(post=post,user=follower.follower,date=post.date_posted,following=user)
      stream.save()
      
post_save.connect(Stream.add_post,sender=Post)
post_save.connect(Likes.user_liked_post,sender=Likes)

post_save.connect(Follow.user_follow,sender=Follow)
post_delete.connect(Follow.user_unfollow,sender=Follow)




# @receiver(pre_delete, sender=Post)
# def delete_post_image(sender, instance, **kwargs):
#     if instance.picture:
#         instance.picture.delete(save=False)
        
        
class Comment(models.Model):
  user = models.ForeignKey(User,on_delete=models.CASCADE)
  post = models.ForeignKey(Post,on_delete=models.CASCADE)
  text = models.TextField(max_length=3000,blank=True,null=True)
  date = models.DateTimeField(auto_now_add=True)
  
  def user_commented_post(sender, instance, *args, **kwargs):
      comment = instance
      post = comment.post
      text_preview = comment.text[:50] if comment.text else ''
      sender = comment.user
      notify = Notification(
          post=post,
          sender=sender,
          recipient=post.user,
          notification_type='comment',
          text_preview = text_preview
          
      )
      notify.save()
      
  def user_uncommented_post(sender, instance, *args, **kwargs):
      comment = instance
      post = comment.post
      sender = comment.user
      notify = Notification.objects.filter(
          post=post,
          sender=sender,
          recipient=post.user,
          notification_type='comment'
      )
      if notify.exists():
          notify.delete()
          
post_save.connect(Comment.user_commented_post,sender=Comment)
post_delete.connect(Comment.user_uncommented_post,sender=Comment)
  
  
  
    

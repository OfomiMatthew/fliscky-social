from django.db import models
from django.contrib.auth.models import User 
from post.models import Post
from django.db.models.signals import post_save 






class Profile(models.Model):
  user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
  first_name = models.CharField(max_length=100,null=True,blank=True)
  last_name = models.CharField(max_length=100,null=True,blank=True)
  location = models.CharField(max_length=100,null=True,blank=True)
  social_url = models.URLField(blank=True,null=True)
  profile_info = models.TextField(blank=True,null=True)
  created = models.DateField(auto_now_add=True)
  favorites = models.ManyToManyField(Post, related_name='favorited_by', blank=True)
  
  # followers = models.ManyToManyField(User, related_name='following', blank=True)
  # following = models.ManyToManyField(User, related_name='followers', blank=True)
  
  picture = models.ImageField(upload_to='profile_pictures',blank=True,null=True)
  
  def get_followers(self):
    return User.objects.filter(following_users__following=self.user)

  def get_following(self):
    return User.objects.filter(follower_users__follower=self.user)
  
  
  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    SIZE = (300, 300)
    if self.picture:
      from PIL import Image
      img = Image.open(self.picture.path)
      img.thumbnail(SIZE, Image.LANCZOS)
      img.save(self.picture.path)
   
  
 
      
      
  def __str__(self):
    return self.user.username 
  
def create_user_profile(sender,instance,created,**kwargs):
  if created:
    Profile.objects.create(user=instance)
    
def save_user_profile(sender,instance,**kwargs):
  instance.profile.save()
  
post_save.connect(create_user_profile,sender=User)
post_save.connect(save_user_profile,sender=User)


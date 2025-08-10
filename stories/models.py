from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete, post_delete
from post.models import Follow



class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='story_user')
    content = models.FileField(upload_to='stories/', max_length=100,null=True, blank=True)
    caption = models.CharField(max_length=255, blank=True,null=True)
    expired = models.BooleanField(default=False)
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Story by {self.user.username} on {self.date_posted}'

    class Meta:
        ordering = ['-date_posted']
        
class StoryStream(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='story_following')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='story_viewer')
    story = models.ManyToManyField(Story, related_name='stories')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Story Stream: {self.user.username} viewed {self.following.username}\'s story on {self.date}'
    
    class Meta:
        ordering = ['-date']
        unique_together = ('user', 'following') 
        
  
    
    def add_post(sender, instance, *args, **kwargs):
        new_story = instance
        user = new_story.user
        followers = Follow.objects.filter(following=user)
        
        streams = []
        for follower in followers:
        # This handles both existing and new streams
            story_stream, created = StoryStream.objects.get_or_create(
            user=follower.follower,
            following=user,
            defaults={'date': new_story.date_posted}
        )
            story_stream.story.add(new_story)
           
# post_save.connect(StoryStream.add_post, sender=Story)
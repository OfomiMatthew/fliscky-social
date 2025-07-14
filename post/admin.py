from django.contrib import admin
from .models import Post,Stream,Follow,Tag

# Register your models here.
admin.site.register(Post)
admin.site.register(Stream)
admin.site.register(Follow)
admin.site.register(Tag)

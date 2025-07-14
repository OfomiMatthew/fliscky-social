from django.urls import path
from .views import new_story,view_story

urlpatterns = [
    path('new-story/', new_story, name='new_story'),
    # path('show-media/<int:stream_id>/', show_media, name='show_media'),
    path('stories/<int:user_id>/', view_story, name='view_story'),
]

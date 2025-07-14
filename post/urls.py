from django.urls import path 
from .views import home,new_post,post_details,get_tags,like,unlike,add_comment,delete_comment,favorite_post,favorites_lists,remove_from_favorites,explore_users

urlpatterns = [
    path('',home,name='home'),
    path('new-post/', new_post, name='new_post'),
    path('post-detail/<uuid:post_id>/',post_details, name='post_details'),
    path('tags/<slug:tag_slug>/',get_tags, name='tags'),
    path('like/<username>/<post_id>',like,name='like'),
    path('unlike/<username>/<post_id>',unlike,name='unlike'),
    path('comment/<str:username>/<str:post_id>/', add_comment, name='add_comment'),
    path('delete-comment/<int:comment_id>/', delete_comment, name='delete_comment'),
    path('favorites/<post_id>/',favorite_post,name='favorite_post'),
    path('favorites_lists/',favorites_lists,name='favorites_lists'),
    path('favorites/remove/<uuid:post_id>/', remove_from_favorites, name='remove_from_favorites'),
    path('explore/users/', explore_users, name='explore_users'),

]

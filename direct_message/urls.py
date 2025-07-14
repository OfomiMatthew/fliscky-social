from django.urls import path
from .views import send_direct,inbox,search_users

urlpatterns = [
    path('inbox/', inbox, name='inbox'),
    path('send-direct/', send_direct, name='send_direct'),
    path('search-users/', search_users, name='search_users'),
]
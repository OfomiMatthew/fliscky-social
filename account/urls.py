from django.urls import path
from .views import SignUp,logout_view,user_profile,edit_profile,follow,followers_list,following_list
from django.contrib.auth import views as authViews 
 
urlpatterns = [
    path('signup/',SignUp,name='signup'),
    path('login/',authViews.LoginView.as_view(template_name='registration/login.html'),name='login'),
    path('logout/',logout_view,name='logout'),
    path('profile/<str:username>/', user_profile, name='profile'),
    path('edit-profile/',edit_profile,name='edit-profile'),
    path('follow/<str:username>/<int:option>/',follow,name='follow'),
    path('followers/<str:username>/', followers_list, name='followers'),
    path('following/<str:username>/', following_list, name='following'),
    #   path('profile/<username>/',user_profile,name='profile-favorites')
]

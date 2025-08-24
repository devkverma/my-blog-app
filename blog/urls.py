from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
    path('', home, name= 'home'),
    path('login/', user_login, name = 'login'),
    path('signup/', user_signup, name = 'signup'),
    path('not_authorized', not_authorized, name = 'not_authorized'),
    path('dashboard/', dashboard, name = 'dashboard'),
    path('logout/', user_logout, name = 'logout'),
    path("users/<uuid:pk>/", user_detail, name="user_detail"),
    path("users/<uuid:pk>/followers/", user_followers, name="user_followers"),
    path("users/<uuid:pk>/following/", user_following, name="user_following"),
    path("users/<uuid:pk>/posts/", user_posts, name="user_posts"),
    path("feed/", feed, name="feed"),
    path("posts/<int:pk>/", post_detail, name="post_detail"),
]
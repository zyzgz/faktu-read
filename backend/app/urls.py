from django.urls import path
from .views import register_user, user_login, user_logout, check_login

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('check_login/', check_login, name='check_login'),
    path('insert-file/', check_login, name='check_login')
]

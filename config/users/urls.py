from django.urls import path

from config.users.views import (
    LogoutView,
    LoginView,
    CreateUserView,
    UserProfileView,
)

app_name = 'users'

urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', UserProfileView.as_view(), name='profile'),
    path('create/', CreateUserView.as_view(), name='user_create'),
]
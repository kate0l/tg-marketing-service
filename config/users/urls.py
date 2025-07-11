from django.urls import path

from config.users.views import (
    LogoutView,
    LoginView,
    CreateUserView,
)

app_name = 'users'

urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('create/', CreateUserView.as_view(), name='user_create'),
]
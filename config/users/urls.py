from django.urls import path

from config.users.views import (
    LogoutView,
    LoginView,
)

app_name = 'users'

urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
]
from django.contrib import messages, auth
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.base import View

from .models import User
from .forms import UserLoginForm


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.add_message(request,
                                 messages.ERROR,
                            'Вы не авторизованы! Пожалуйста, выполните вход.')
            return redirect(reverse('login'))
        return redirect(reverse('main_index'))

    def post(self, request, *args, **kwargs):
        messages.add_message(request, messages.INFO, 'Вы разлогинены')
        auth.logout(request)
        return redirect(reverse('main_index'))
    
    
class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = UserLoginForm()
        return render(
            request,
            'login.html',
            {'form': form}
        )
        
    def post(self, request, *args, **kwargs):
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                messages.add_message(request, messages.SUCCESS, 'Вы залогинены')
                return redirect(reverse('main_index'))
        return render(request, 'login.html', {'form': form})
   

class UserProfileView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.add_message(request,
                                 messages.ERROR,
                            'Вы не авторизованы! Пожалуйста, выполните вход.')
            return redirect(reverse('login'))
        user = request.user
        return render(
            request,
            'users/profile.html',
            {'user': user}
        )
        

class CreateUserView(View):
    ...
from django.contrib import messages, auth
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.base import View

from .models import User


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
from django.contrib import messages, auth
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.base import View

from .models import User
from .forms import UserLoginForm, UserRegForm, UserUpdateForm

from config.group_channels.forms import CreateGroupForm, UpdateGroupForm


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
        create_form = CreateGroupForm()
        update_form = UpdateGroupForm()
        user = request.user
        groups = user.user_group.all()
        return render(
            request,
            'users/profile.html',
            {'user': user,
             'create_form': create_form,
             'update_form': update_form,
             'groups': groups}
        )
        

class UserRegister(View):
    def post(self, request, *args, **kwargs):
        form = UserRegForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Пользователь успешно зарегистрирован')
            return redirect(reverse('users:login'))
        return render(request, 'users/register.html', {'form': form})
    
    def get(self, request, *args, **kwargs):
        form = UserRegForm()
        return render(
            request,
            'users/register.html',
            {'form': form}
        )
        

class UserUpdate(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.add_message(request,
                                 messages.ERROR,
                            'Вы не авторизованы! Пожалуйста, выполните вход.')
            return redirect(reverse('login'))
        if request.user.username == kwargs.get('username'):
            form = UserUpdateForm(initial={
                'username': request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'avatar_image': request.user.avatar_image,
                'email': request.user.email,
                'bio': request.user.bio,
            })
            return render(
                request,
                'users/update.html',
                {'form': form,
                 'username': request.user.username
                }
            )
        messages.add_message(request,
                             messages.ERROR,
                        'У вас нет прав для изменения другого пользователя.')
        return redirect(reverse('users:profile'))
    
    def post(self, request, *args, **kwargs):
        username = kwargs.get('username')
        user = User.objects.get(username=username)
        form = UserUpdateForm(data=request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Профиль успешно изменен')
            return redirect(reverse('users:profile'))
        return render(
            request,
            'users/update.html',
            {'form': form}
        )
